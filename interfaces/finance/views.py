from django.db import models
from django.db.models import Sum, Count, Q  #
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP
from collections import OrderedDict
from django.utils.timezone import now, make_aware, is_naive
from django.utils.dateparse import parse_date
from django.db.models.functions import TruncMonth
from django.core.cache import cache
import calendar
from datetime import datetime, timedelta
from django.utils import timezone
from interfaces.members.models import Member, PaymentHistory
from interfaces.expense.models import Expense


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    try:
        start = request.GET.get("start_date")
        end = request.GET.get("end_date")

        # Build cache key
        cache_key = f"dashboard_stats_{start}_{end}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        if not start or not end:
            end_date = now().date()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            if is_naive(start_date):
                start_date = make_aware(start_date)
            if is_naive(end_date):
                end_date = make_aware(end_date)

        raw_revenue = PaymentHistory.objects.filter(
            transaction_date__range=[start_date, end_date]
        ).aggregate(total=Sum("payment_amount"))["total"]

        raw_expenses = Expense.objects.filter(
            date__range=[start_date.date(), end_date.date()]
        ).aggregate(total=Sum("amount"))["total"]

        total_revenue = Decimal(raw_revenue or 0).quantize(Decimal("0.01"))
        total_expenses = Decimal(raw_expenses or 0).quantize(Decimal("0.01"))
        gross_profit = (total_revenue * Decimal("0.25")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        net_profit = (total_revenue - total_expenses).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        current_time = now()
        new_members = Member.objects.filter(membership_start__date__range=[start_date.date(), end_date.date()]).count()
        active_members = Member.objects.filter(membership_end__gte=current_time, is_blocked=False).count()
        expiring = Member.objects.filter(membership_end__range=[current_time, current_time + timedelta(days=7)]).count()
        renewals = PaymentHistory.objects.filter(
            transaction_type="renewal",
            transaction_date__range=[start_date, end_date]
        ).count()
        new_signups_today = Member.objects.filter(membership_start__date=now().date()).count()

        response_data = {
            "total_revenue": float(total_revenue),
            "total_expenses": float(total_expenses),
            "gross_profit": float(gross_profit),
            "net_profit": float(net_profit),
            "new_members": new_members,
            "active_members": active_members,
            "expiring_soon": expiring,
            "renewals": renewals,
            "new_signups": new_signups_today,
            "range": {
                "start": str(start_date.date()),
                "end": str(end_date.date()),
            },
        }

        cache.set(cache_key, response_data, timeout=180)
        return Response(response_data)

    except Exception as e:
        print("🔥 ERROR in dashboard_stats:", e)
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_enrollment_and_revenue_summary(request):
    start_date = parse_date(request.GET.get("start"))
    end_date = parse_date(request.GET.get("end"))

    cache_key = f"monthly_summary_{start_date}_{end_date}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    queryset = PaymentHistory.objects.all()
    if start_date:
        queryset = queryset.filter(transaction_date__date__gte=start_date)
    if end_date:
        queryset = queryset.filter(transaction_date__date__lte=end_date)

    monthly_data = (
        queryset
        .annotate(month=TruncMonth("transaction_date"))
        .values("month")
        .annotate(
            total_revenue=Sum("payment_amount"),
            enrollments=Count("id", filter=Q(transaction_type="initial"))
        )
        .order_by("month")
    )

    result = OrderedDict()
    if start_date and end_date:
        current = start_date
        while current <= end_date:
            month_name = calendar.month_name[current.month]
            result[month_name] = {
                "month": month_name,
                "enrollments": 0,
                "revenue": 0.0,
            }
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

    for item in monthly_data:
        month_name = item["month"].strftime("%B")
        result[month_name] = {
            "month": month_name,
            "enrollments": item["enrollments"],
            "revenue": float(item["total_revenue"] or 0),
        }

    response_data = list(result.values())
    cache.set(cache_key, response_data, timeout=180)
    return Response(response_data)




#     # Save the workbook to a BytesIO object
#     output = BytesIO()            



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def membership_plan_report(request):
    start_date = parse_date(request.GET.get("start"))
    end_date = parse_date(request.GET.get("end"))

    if not start_date or not end_date:
        return Response({"detail": "start and end are required in YYYY-MM-DD format"}, status=400)

    cache_key = f"membership_report_{start_date}_{end_date}"
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)

    start_datetime = make_aware(datetime.combine(start_date, datetime.min.time()))
    end_datetime = make_aware(datetime.combine(end_date + timedelta(days=1), datetime.min.time()))

    # Total Enrollments
    total_enrollments = PaymentHistory.objects.filter(
        transaction_type="initial",
        transaction_date__range=(start_datetime, end_datetime)
    ).count()

    # Total Revenue
    total_revenue = PaymentHistory.objects.filter(
        transaction_date__range=(start_datetime, end_datetime)
    ).aggregate(total=Sum("payment_amount"))["total"] or 0

    # Most Popular Plan
    popular_plan = PaymentHistory.objects.filter(
        transaction_type="initial",
        transaction_date__range=(start_datetime, end_datetime)
    ).values("plan_name_snapshot").annotate(
        count=Count("id")
    ).order_by("-count").first()

    response_data = {
        "total_enrollments": total_enrollments,
        "total_revenue": float(total_revenue),
        "most_popular_plan": popular_plan["plan_name_snapshot"] if popular_plan else "N/A",
    }

    cache.set(cache_key, response_data, timeout=60 * 15)
    return Response(response_data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def enrollment_trends_chart(request):
    start_date = parse_date(request.GET.get("start"))
    end_date = parse_date(request.GET.get("end"))

    if not start_date or not end_date:
        return Response({"detail": "Start and end dates are required"}, status=400)

    queryset = PaymentHistory.objects.filter(
        transaction_type="initial",
        transaction_date__date__gte=start_date,
        transaction_date__date__lte=end_date,
    )

    monthly_data = (
        queryset
        .annotate(month=TruncMonth("transaction_date"))
        .values("month")
        .annotate(enrollments=Count("id"))
        .order_by("month")
    )

    result = OrderedDict()
    current = start_date.replace(day=1)
    while current <= end_date:
        month_name = current.strftime("%B")
        result[month_name] = { "month": month_name, "enrollments": 0 }
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    for item in monthly_data:
        month_name = item["month"].strftime("%B")
        result[month_name] = {
            "month": month_name,
            "enrollments": item["enrollments"]
        }

    return Response(list(result.values()))



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def revenue_by_plan(request):
    start_date = parse_date(request.GET.get("start"))
    end_date = parse_date(request.GET.get("end"))

    if not start_date or not end_date:
        return Response({"detail": "Start and end dates are required"}, status=400)

    # Convert to datetime range
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date + timedelta(days=1), datetime.min.time())

    # Aggregate revenue grouped by plan name snapshot
    revenue_data = (
        PaymentHistory.objects.filter(
            transaction_date__range=(start_datetime, end_datetime)
        )
        .values("plan_name_snapshot")
        .annotate(revenue=Sum("payment_amount"))
        .order_by("-revenue")
    )

    # Rename keys to match frontend expectations
    response = [
        {
            "plan": item["plan_name_snapshot"],
            "revenue": float(item["revenue"] or 0)
        }
        for item in revenue_data
    ]

    return Response(response)




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reports_overview(request):
    try:
        start = request.GET.get("start_date")
        end = request.GET.get("end_date")

        if not start or not end:
            return Response({"detail": "start_date and end_date are required"}, status=400)

        cache_key = f"reports_overview_{start}_{end}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")

        if is_naive(start_dt):
            start_dt = make_aware(start_dt)
        if is_naive(end_dt):
            end_dt = make_aware(end_dt)

        # Total revenue from payments
        total_revenue = PaymentHistory.objects.filter(
            transaction_date__range=[start_dt, end_dt]
        ).aggregate(total=Sum("payment_amount"))["total"] or 0

        # Total expenses
        total_expenses = Expense.objects.filter(
            date__range=[start_dt.date(), end_dt.date()]
        ).aggregate(total=Sum("amount"))["total"] or 0

        # Active members
        current_time = now()
        active_members = Member.objects.filter(
            membership_end__gte=current_time, is_blocked=False
        ).count()

        data = {
            "total_revenue": float(total_revenue),
            "total_expenses": float(total_expenses),
            "active_members": active_members,
        }

        cache.set(cache_key, data, timeout=180)
        return Response(data)

    except Exception as e:
        print("🔥 Error in reports_overview:", str(e))
        return Response({"error": str(e)}, status=500)
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def expense_category_breakdown(request):
    try:
        start = request.GET.get("start")
        end = request.GET.get("end")

        if not start or not end:
            return Response({"detail": "start and end are required"}, status=400)

        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")

        if is_naive(start_date):
            start_date = make_aware(start_date)
        if is_naive(end_date):
            end_date = make_aware(end_date)

        # ORM aggregation
        breakdown = (
            Expense.objects.filter(date__range=(start_date.date(), end_date.date()))
            .values("category")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        response_data = [
            {
                "category": item["category"],
                "total": float(item["total"] or 0),
            }
            for item in breakdown
        ]

        return Response(response_data)

    except Exception as e:
        print("🔥 Error in expense_category_breakdown:", str(e))
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_revenue_chart(request):
    try:
        start = parse_date(request.GET.get("start"))
        end = parse_date(request.GET.get("end"))

        if not start or not end:
            return Response({"detail": "Start and end dates are required"}, status=400)

        cache_key = f"monthly_revenue:{start}:{end}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        start_dt = make_aware(datetime.combine(start, datetime.min.time()))
        end_dt = make_aware(datetime.combine(end + timedelta(days=1), datetime.min.time()))

        monthly_data = (
            PaymentHistory.objects.filter(transaction_date__range=(start_dt, end_dt))
            .annotate(month=TruncMonth("transaction_date"))
            .values("month")
            .annotate(revenue=Sum("payment_amount"))
            .order_by("month")
        )

        result = OrderedDict()
        current = start.replace(day=1)
        while current <= end:
            month_name = current.strftime("%B")
            result[month_name] = {"month": month_name, "revenue": 0}
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        for item in monthly_data:
            month = item["month"].strftime("%B")
            result[month] = {
                "month": month,
                "revenue": float(item["revenue"] or 0),
            }

        final_data = list(result.values())
        cache.set(cache_key, final_data, timeout=60 * 10)  # cache for 10 minutes

        return Response(final_data)

    except Exception as e:
        print("🔥 ERROR in monthly_revenue_chart:", str(e))
        return Response({"error": str(e)}, status=500)




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def membership_growth_chart(request):
    try:
        # Parse and make start & end aware
        start_date = request.GET.get("start")
        end_date = request.GET.get("end")

        if not start_date or not end_date:
            return Response({"detail": "Start and end dates are required"}, status=400)

        start = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
        end = make_aware(datetime.strptime(end_date, "%Y-%m-%d")) + timedelta(days=1)

        # Annotate by month based on membership_start
        monthly_counts = (
            Member.objects.filter(membership_start__range=(start, end))
            .annotate(month=TruncMonth("membership_start"))
            .values("month")
            .annotate(members=Count("id"))
            .order_by("month")
        )

        # Fill missing months
        result = OrderedDict()
        current = start.replace(day=1)
        while current < end:
            month_name = current.strftime("%B")
            result[month_name] = {"month": month_name, "members": 0}
            current_month = current.month
            if current_month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current_month + 1)

        for item in monthly_counts:
            month_name = item["month"].strftime("%B")
            result[month_name]["members"] = item["members"]

        return Response(list(result.values()))

    except Exception as e:
        return Response({"detail": str(e)}, status=500)
    




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def membership_status_counts(request):
    current_time = now()
    expiring_threshold = current_time + timedelta(days=5)

    total = Member.objects.count()
    blocked = Member.objects.filter(is_blocked=True).count()
    expired = Member.objects.filter(
        is_blocked=False,
        membership_end__lt=current_time
    ).count()
    payment_due = Member.objects.filter(
        is_blocked=False,
        membership_end__gte=current_time,
        membership_plan__isnull=False,
        amount_paid__lt=models.F("membership_plan__price")
    ).count()
    expiring = Member.objects.filter(
        is_blocked=False,
        membership_end__gt=current_time,
        membership_end__lte=expiring_threshold,
        amount_paid__gte=models.F("membership_plan__price")  # Optional: exclude dues from expiring
    ).count()
    active = Member.objects.filter(
        is_blocked=False,
        membership_end__gt=expiring_threshold,
        amount_paid__gte=models.F("membership_plan__price")
    ).count()

    return Response({
        "total": total,
        "blocked": blocked,
        "expired": expired,
        "payment_due": payment_due,
        "expiring": expiring,
        "active": active,
    })









@api_view(["GET"])
@permission_classes([IsAuthenticated])
def renewals_signups_chart(request):
    from django.db.models.functions import TruncMonth
    from django.utils.timezone import make_aware
    from collections import OrderedDict
    from datetime import datetime, timedelta

    start = request.GET.get("start")
    end = request.GET.get("end")
    if not start or not end:
        return Response({"detail": "Start and end required"}, status=400)

    start_dt = make_aware(datetime.strptime(start, "%Y-%m-%d"))
    end_dt = make_aware(datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1))

    from interfaces.members.models import PaymentHistory

    data = (
        PaymentHistory.objects
        .filter(transaction_date__range=(start_dt, end_dt))
        .annotate(month=TruncMonth("transaction_date"))
        .values("month")
        .annotate(
            renewals=Count("id", filter=Q(transaction_type="renewal")),
            signups=Count("id", filter=Q(transaction_type="initial")),
        )
        .order_by("month")
    )

    result = []
    for row in data:
        result.append({
            "month": row["month"].strftime("%B"),
            "renewals": row["renewals"],
            "signups": row["signups"],
        })

    return Response(result)





@api_view(["GET"])
@permission_classes([IsAuthenticated])
def plan_distribution_chart(request):
    today = now()

    data = (
        Member.objects
        .filter(is_blocked=False, membership_end__gte=today, membership_plan__isnull=False)
        .values("membership_plan__name")
        .annotate(members=Count("id"))
        .order_by("-members")
    )

    result = [
        {
            "plan": item["membership_plan__name"],
            "members": item["members"]
        }
        for item in data
    ]

    return Response(result)







@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sales_report_quick_stats(request):
    start = request.GET.get("start")
    end = request.GET.get("end")

    if not start or not end:
        return Response({"detail": "Start and end dates required"}, status=400)

    start_dt = make_aware(datetime.strptime(start, "%Y-%m-%d"))
    end_dt = make_aware(datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1))

    # 1. Total Revenue: sum of all payments in range
    total_revenue = PaymentHistory.objects.filter(
        transaction_date__range=(start_dt, end_dt)
    ).aggregate(total=Sum("payment_amount"))["total"] or 0

    # 2. Total Sales: count of payment events (initial enrollments and renewals)
    total_sales = PaymentHistory.objects.filter(
        transaction_date__range=(start_dt, end_dt),
        transaction_type__in=["initial", "renewal"]
    ).count()

    # 3. Pending Payments: sum of remaining_balance for active members
    today = timezone.now()

    pending_payments = Member.objects.filter(
        is_blocked=False,
        membership_end__gte=today,
        remaining_balance__gt=0
    ).aggregate(total=Sum("remaining_balance"))["total"] or 0

    # 4. Top Selling Plan: most purchased plan (snapshot name)
    top_plan = (
        PaymentHistory.objects.filter(
            transaction_date__range=(start_dt, end_dt),
            transaction_type__in=["initial", "renewal"]
        )
        .values("plan_name_snapshot")
        .annotate(count=Count("id"))
        .order_by("-count")
        .first()
    )

    return Response({
        "total_revenue": total_revenue,
        "total_sales": total_sales,
        "pending_payments": pending_payments,
        "top_selling_plan": top_plan["plan_name_snapshot"] if top_plan else None,
    })





@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sales_over_time_chart(request):
    start = request.GET.get("start")
    end = request.GET.get("end")

    if not start or not end:
        return Response({"detail": "Start and end dates are required"}, status=400)

    start_dt = make_aware(datetime.strptime(start, "%Y-%m-%d"))
    end_dt = make_aware(datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1))

    # Query: Sum payments month-wise
    monthly_data = (
        PaymentHistory.objects.filter(transaction_date__range=(start_dt, end_dt))
        .annotate(month=TruncMonth("transaction_date"))
        .values("month")
        .annotate(sales=Sum("payment_amount"))
        .order_by("month")
    )

    # Fill missing months (so chart always shows smooth line even if no sales)
    result = OrderedDict()
    current = start_dt.replace(day=1)
    while current < end_dt:
        month_name = current.strftime("%B")
        result[month_name] = {"month": month_name, "sales": 0}
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    for record in monthly_data:
        month_name = record["month"].strftime("%B")
        if month_name in result:
            result[month_name]["sales"] = record["sales"]

    return Response(list(result.values()))




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sales_by_plan_chart(request):
    start = request.GET.get("start")
    end = request.GET.get("end")

    if not start or not end:
        return Response({"detail": "Start and end dates required"}, status=400)

    start_dt = make_aware(datetime.strptime(start, "%Y-%m-%d"))
    end_dt = make_aware(datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1))

    plan_sales = (
        PaymentHistory.objects.filter(
            transaction_date__range=(start_dt, end_dt),
            transaction_type__in=["initial", "renewal"]
        )
        .values("plan_name_snapshot")
        .annotate(sales=Sum("payment_amount"))
        .order_by("-sales")
    )

    response_data = [
        {"plan": item["plan_name_snapshot"], "sales": item["sales"] or 0}
        for item in plan_sales
    ]

    return Response(response_data)











@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pending_renewals_chart(request):
    start = request.GET.get("start")
    end = request.GET.get("end")

    if not start or not end:
        return Response({"detail": "Start and end dates required"}, status=400)

    start_dt = make_aware(datetime.strptime(start, "%Y-%m-%d"))
    end_dt = make_aware(datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1))

    monthly_pending = (
        Member.objects.filter(membership_end__range=(start_dt, end_dt), is_blocked=False)
        .annotate(month=TruncMonth("membership_end"))
        .values("month")
        .annotate(pendingRenewals=Count("id"))
        .order_by("month")
    )

    # Fill missing months
    result = []
    current = start_dt.replace(day=1)
    while current < end_dt:
        month_name = current.strftime("%B")
        count = next((item["pendingRenewals"] for item in monthly_pending if item["month"].strftime("%B") == month_name), 0)
        result.append({"month": month_name, "pendingRenewals": count})
        
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    return Response(result)





@api_view(["GET"])
@permission_classes([IsAuthenticated])
def member_quick_statistics(request):
    total_members = Member.objects.filter(is_blocked=False).count()

    male_members = Member.objects.filter(
        is_blocked=False, gender='male'
    ).count()

    female_members = Member.objects.filter(
        is_blocked=False, gender='female'
    ).count()

    return Response({
        "total_members": total_members,
        "male_members": male_members,
        "female_members": female_members,
    })











@api_view(["GET"])
@permission_classes([IsAuthenticated])
def gender_distribution_chart(request):
    start = request.GET.get("start")
    end = request.GET.get("end")

    if not start or not end:
        return Response({"detail": "Start and end dates are required"}, status=400)

    # Parse and combine to datetime
    start_parsed = parse_date(start)
    end_parsed = parse_date(end)

    if not start_parsed or not end_parsed:
        return Response({"detail": "Invalid start or end date"}, status=400)

    start_dt = datetime.combine(start_parsed, datetime.min.time())
    end_dt = datetime.combine(end_parsed, datetime.max.time())  # Use max time to fully include end day

    # Make timezone-aware if needed
    if is_naive(start_dt):
        start_dt = make_aware(start_dt)
    if is_naive(end_dt):
        end_dt = make_aware(end_dt)

    members = Member.objects.filter(
        membership_start__range=(start_dt, end_dt),
        is_blocked=False
    )

    gender_counts = members.values("gender").annotate(count=Count("id"))

    result = {
        "male": 0,
        "female": 0,
        "other": 0,
    }

    for item in gender_counts:
        gender = item["gender"]
        count = item["count"]
        if gender == "male":
            result["male"] = count
        elif gender == "female":
            result["female"] = count
        elif gender == "other":
            result["other"] = count

    return Response(result)




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def age_gender_breakdown_chart(request):
    start = request.GET.get("start")
    end = request.GET.get("end")

    if not start or not end:
        return Response({"detail": "Start and end dates are required"}, status=400)

    start_parsed = parse_date(start)
    end_parsed = parse_date(end)

    if not start_parsed or not end_parsed:
        return Response({"detail": "Invalid start or end date"}, status=400)

    start_dt = datetime.combine(start_parsed, datetime.min.time())
    end_dt = datetime.combine(end_parsed, datetime.max.time())

    if is_naive(start_dt):
        start_dt = make_aware(start_dt)
    if is_naive(end_dt):
        end_dt = make_aware(end_dt)

    members = Member.objects.filter(
        membership_start__range=(start_dt, end_dt),
        is_blocked=False,
    )

    teen_boys = members.filter(gender="male", age__gte=13, age__lte=19).count()
    teen_girls = members.filter(gender="female", age__gte=13, age__lte=19).count()
    young_men = members.filter(gender="male", age__gte=20, age__lte=49).count()
    young_women = members.filter(gender="female", age__gte=20, age__lte=49).count()
    men_50_plus = members.filter(gender="male", age__gte=50).count()
    women_50_plus = members.filter(gender="female", age__gte=50).count()

    result = [
        {"category": "Teen Boys", "count": teen_boys},
        {"category": "Teen Girls", "count": teen_girls},
        {"category": "Young Men (20-49)", "count": young_men},
        {"category": "Young Women (20-49)", "count": young_women},
        {"category": "Men 50+", "count": men_50_plus},
        {"category": "Women 50+", "count": women_50_plus},
    ]

    return Response(result)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def expense_summary_stats(request):
    start = request.GET.get("start")
    end = request.GET.get("end")

    if not start or not end:
        return Response({"detail": "Start and End dates are required."}, status=400)

    start_date = parse_date(start)
    end_date = parse_date(end)

    expenses = Expense.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )

    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0

    # Get category-wise expense total and pick the largest category
    largest_category = (
        expenses.values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
        .first()
    )

    return Response({
        "total_expenses": total_expenses,
        "largest_category": largest_category["category"] if largest_category else None,
    })







@api_view(["GET"])
@permission_classes([IsAuthenticated])
def expense_category_breakdown(request):
    start = request.GET.get("start")
    end = request.GET.get("end")

    if not start or not end:
        return Response({"detail": "Start and End dates are required."}, status=400)

    start_date = parse_date(start)
    end_date = parse_date(end)

    if not start_date or not end_date:
        return Response({"detail": "Invalid date format."}, status=400)

    expenses = Expense.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )

    category_summary = (
        expenses.values('category')
        .annotate(total_amount=Sum('amount'))
        .order_by('-total_amount')
    )

    return Response(category_summary)





@api_view(["GET"])
@permission_classes([IsAuthenticated])
def expense_trends_chart(request):
    start = request.GET.get("start")
    end = request.GET.get("end")

    if not start or not end:
        return Response({"detail": "Start and End dates are required."}, status=400)

    start_date = parse_date(start)
    end_date = parse_date(end)

    if not start_date or not end_date:
        return Response({"detail": "Invalid dates provided."}, status=400)

    # Make sure they're timezone-aware
    start_dt = make_aware(datetime.combine(start_date, datetime.min.time()))
    end_dt = make_aware(datetime.combine(end_date + timedelta(days=1), datetime.min.time()))

    # Group expenses month-wise
    monthly_data = (
        Expense.objects.filter(date__range=(start_date, end_date))
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(expenses=Sum('amount'))
        .order_by('month')
    )

    # Filling missing months
    result = OrderedDict()
    current = start_date.replace(day=1)
    while current <= end_date:
        month_name = current.strftime("%B")
        result[month_name] = {"month": month_name, "expenses": 0}
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    for entry in monthly_data:
        month_name = entry["month"].strftime("%B")
        result[month_name] = {
            "month": month_name,
            "expenses": float(entry["expenses"]) if entry["expenses"] else 0
        }

    return Response(list(result.values()))