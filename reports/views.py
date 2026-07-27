import json
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .models import Renewal, ReportMeta, Snapshot


# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None
    next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard'
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = 'dashboard'

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)
        error = 'Invalid username or password'

    return render(request, 'reports/login.html', {'error': error, 'next': next_url})


def logout_view(request):
    logout(request)
    return redirect('login')


def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


# --------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------

@login_required(login_url='login')
@ensure_csrf_cookie
def dashboard_view(request):
    return render(request, 'reports/index.html', {'username': request.user.username})


# --------------------------------------------------------------------------
# Report API — this is what makes the report shared across PCs.
# One PC POSTs the processed report to /api/save-report/, and every PC
# (including ones that never uploaded anything) reads the same data back
# from GET /api/get-report/.
# --------------------------------------------------------------------------

@login_required(login_url='login')
def get_report(request):
    renewals = list(
        Renewal.objects.all().order_by('recharge_date').values(
            'customer_id', 'customer_name', 'manager', 'bu_code',
            'recharge_date', 'package', 'amount', 'plan_name', 'period',
            'fiscal_year', 'speed', 'churn_days',
        )
    )
    for r in renewals:
        if r['recharge_date']:
            r['recharge_date'] = r['recharge_date'].isoformat()
        if r['amount'] is not None:
            r['amount'] = float(r['amount'])

    meta = ReportMeta.objects.filter(id=1).first()

    return JsonResponse({
        'renewals': renewals,
        'churnBUCounts': meta.churn_bu_counts if meta else {},
        'churnManagerCounts': meta.churn_manager_counts if meta else {},
        'updatedAt': meta.updated_at.isoformat() if meta else None,
        'updatedBy': meta.updated_by if meta else None,
    })


@login_required(login_url='login')
@require_http_methods(['POST'])
def save_report(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    renewals = payload.get('renewals', [])
    churn_bu = payload.get('churnBUCounts', {}) or {}
    churn_mgr = payload.get('churnManagerCounts', {}) or {}

    with transaction.atomic():
        Renewal.objects.all().delete()

        objs = []
        for r in renewals:
            date_str = (r.get('date') or '')[:10] or None
            objs.append(Renewal(
                customer_id=r.get('id', '') or '',
                customer_name=r.get('name', '') or '',
                manager=r.get('manager', '') or '',
                bu_code=r.get('buCode', '') or '',
                recharge_date=date_str,
                package=r.get('package', '') or '',
                amount=r.get('amount') or 0,
                plan_name=r.get('plan', '') or '',
                period=r.get('period', '') or '',
                fiscal_year=r.get('fiscalYear', '') or '',
                speed=r.get('speed', '') or '',
                churn_days=r.get('churnDays', '') or '',
            ))
        Renewal.objects.bulk_create(objs, batch_size=500)

        meta, _ = ReportMeta.objects.get_or_create(id=1)
        meta.churn_bu_counts = churn_bu
        meta.churn_manager_counts = churn_mgr
        meta.updated_by = request.user.username
        meta.save()

    return JsonResponse({'success': True, 'count': len(renewals)})


# --------------------------------------------------------------------------
# Snapshots API
# --------------------------------------------------------------------------

@login_required(login_url='login')
@require_http_methods(['POST'])
def save_snapshot(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    date = payload.get('date')
    data = payload.get('data', [])
    if not date:
        return JsonResponse({'error': 'date is required'}, status=400)

    total_renewals = len(data)
    total_revenue = sum(Decimal(str(r.get('amount', 0) or 0)) for r in data)

    Snapshot.objects.update_or_create(
        snapshot_date=date,
        defaults={
            'total_renewals': total_renewals,
            'total_revenue': total_revenue,
            'data': data,
        }
    )
    return JsonResponse({'success': True})


@login_required(login_url='login')
def get_snapshots(request):
    snaps = list(
        Snapshot.objects.all().values(
            'snapshot_date', 'saved_at', 'total_renewals', 'total_revenue'
        )
    )
    for s in snaps:
        s['snapshot_date'] = s['snapshot_date'].isoformat()
        s['saved_at'] = s['saved_at'].isoformat()
        s['total_revenue'] = float(s['total_revenue'])
    return JsonResponse(snaps, safe=False)


@login_required(login_url='login')
def get_snapshot(request, date):
    try:
        snap = Snapshot.objects.get(snapshot_date=date)
    except Snapshot.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    return JsonResponse({'data': snap.data})


@login_required(login_url='login')
@require_http_methods(['POST'])
def clear_snapshots(request):
    Snapshot.objects.all().delete()
    return JsonResponse({'success': True})
