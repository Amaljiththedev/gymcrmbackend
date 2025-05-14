from interfaces.members.models import Attendance, Member

# interfaces/members/services/biometric_sync.py
from django.utils import timezone # adjust your import paths
from datetime import date
from zk import ZK, const
def sync_attendance_from_essl(ip="192.168.1.102", port=4370):
    zk = ZK(ip, port=port, timeout=10)
    try:
        conn = zk.connect()
        conn.disable_device()

        logs = conn.get_attendance()

        for log in logs:
            uid = log.user_id
            punch_time = log.timestamp.date()

            try:
                member = Member.objects.get(biometric_id=uid)
                if member.membership_status == "active":
                    Attendance.objects.get_or_create(member=member, attendance_date=punch_time)
                    print(f"✅ {member} granted access.")
                else:
                    print(f"⛔ {member} denied - Status: {member.membership_status}")
            except Member.DoesNotExist:
                print(f"❌ Biometric ID {uid} not linked to any member.")

        conn.enable_device()
        conn.disconnect()
        print("✅ Sync completed.")
    except Exception as e:
        print("❌ Sync failed:", e)