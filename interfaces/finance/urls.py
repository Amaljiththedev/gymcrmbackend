from django.urls import path
from .views import age_gender_breakdown_chart, dashboard_stats, enrollment_trends_chart, expense_category_breakdown, expense_summary_stats, expense_trends_chart, gender_distribution_chart, member_quick_statistics, membership_growth_chart, membership_plan_report, membership_status_counts, monthly_enrollment_and_revenue_summary, monthly_revenue_chart, pending_renewals_chart, plan_distribution_chart, renewals_signups_chart, reports_overview, revenue_by_plan, sales_by_plan_chart, sales_over_time_chart, sales_report_quick_stats 

urlpatterns = [
    path("stats/", dashboard_stats, name="dashboard-stats"),
        path(
        "monthly-summary/",
        monthly_enrollment_and_revenue_summary,
        name="monthly-enrollment-revenue-summary"
    ),
    path("reports/membership-plan/", membership_plan_report, name="membership_plan_report"),
    path("reports/enrollment-chart/", enrollment_trends_chart, name="enrollment_trends_chart"),
    path("reports/revenue-by-plan/", revenue_by_plan, name="revenue_by_plan"),
    path("reports-overview", reports_overview, name="reports_overview"),
    path("expense-category-breakdown", expense_category_breakdown, name="expense_category_breakdown"),
    path("monthly-revenue/",  monthly_revenue_chart, name="monthly_revenue_chart"),
    path("membership-growth-chart/", membership_growth_chart, name="membership-growth-chart"),
    path("membership-status-counts/", membership_status_counts, name="membership-status-counts"),
    path("renewals-signups-chart/", renewals_signups_chart, name="renewals-signups-chart"),
    path("plan-distribution-chart/", plan_distribution_chart, name="plan-distribution-chart"),
    path("sales-report-quick-stats/", sales_report_quick_stats, name="sales-report-quick-stats"),
    path("sales-over-time-chart/", sales_over_time_chart, name="sales-over-time-chart"),
    path("sales-by-plan-chart/", sales_by_plan_chart, name="sales-by-plan-chart"),
    path("pending-renewals-chart/", pending_renewals_chart, name="pending-renewals-chart"),
    path("member-quick-statistics/", member_quick_statistics, name="member-quick-statistics"),
    path("gender-distribution-chart/", gender_distribution_chart, name="gender-distribution-chart"),
    path("age-gender-breakdown-chart/", age_gender_breakdown_chart, name="age-gender-breakdown-chart"),
    path("expense-summary-stats/", expense_summary_stats, name="expense-summary-stats"),
    path('expense-category-breakdown/', expense_category_breakdown, name='expense-category-breakdown'),
    path('expense-trends-chart/', expense_trends_chart, name='expense-trends-chart'),

]
