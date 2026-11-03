from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models import (
    User, Role, Permission, Department, ITService, Asset,
    Ticket, TicketComment, TicketStatusHistory, TicketAssignment,
    Incident, ProblemRecord, KnownError,
    ChangeRequest, ChangeHistory, SecurityIncident, SecurityTimeline, SecurityEvidence,
    KnowledgeArticle, SLAPolicy, SLATracking, AutomationRule,
    MonitoringDevice, MonitoringMetric, MonitoringAlert,
    AuditLog, PriorityLevel, ImpactLevel, UrgencyLevel,
    TicketStatus, CommentType, AssetType, AssetStatus,
    ServiceTier, ServiceStatus, IncidentSeverity, IncidentStatus,
    ChangeType, ChangeRisk, ChangeStatus, SecurityCategory,
    SecuritySeverity, SecurityStatus, ArticleStatus, TriggerEvent
)

def seed_database(db: Session):
    # Check if already seeded
    if db.query(User).count() > 0:
        print("Database already contains data, skipping seed.")
        return

    print("Seeding initial enterprise ITSM data...")
    now = datetime.now(timezone.utc)

    # 1. Departments
    dept_it = Department(name="IT Operations & Infrastructure", code="IT-OPS", description="Enterprise infrastructure, servers, and tier-1/2/3 support", manager_name="Sarah Jenkins")
    dept_eng = Department(name="Software Engineering", code="ENG", description="Core product engineering and platform architecture", manager_name="David Chen")
    dept_hr = Department(name="Human Resources", code="HR", description="People operations and corporate talent", manager_name="Emily Davis")
    dept_fin = Department(name="Finance & Accounting", code="FIN", description="Financial operations and treasury", manager_name="Robert Miller")
    dept_sec = Department(name="Information Security", code="INFOSEC", description="Cybersecurity, threat hunting, and compliance", manager_name="Elena Vance")
    
    db.add_all([dept_it, dept_eng, dept_hr, dept_fin, dept_sec])
    db.flush()

    # 2. Roles
    role_admin = Role(name="System Administrator", description="Full system configuration and governance")
    role_manager = Role(name="IT Operations Manager", description="Supervise operations, approvals, and SLA enforcement")
    role_tech = Role(name="IT Support Technician", description="Triage, troubleshoot, and resolve incidents and requests")
    role_emp = Role(name="Employee", description="Standard corporate user submitting and tracking IT requests")
    role_sec = Role(name="Security Analyst", description="Investigate security events and cybersecurity incidents")
    role_auditor = Role(name="Auditor", description="Read-only compliance and audit history inspection")

    db.add_all([role_admin, role_manager, role_tech, role_emp, role_sec, role_auditor])
    db.flush()

    # 3. Users representing the 6 primary roles
    user_admin = User(
        email="admin@company.com", username="admin", full_name="System Administrator",
        hashed_password=get_password_hash("Admin123!"), department_id=dept_it.id, is_active=True
    )
    user_admin.roles.append(role_admin)

    user_mgr = User(
        email="sarah.manager@company.com", username="sarah.manager", full_name="Sarah Jenkins (Manager)",
        hashed_password=get_password_hash("Manager123!"), department_id=dept_it.id, is_active=True
    )
    user_mgr.roles.append(role_manager)

    user_tech = User(
        email="alex.tech@company.com", username="alex.tech", full_name="Alex Rivera (Technician)",
        hashed_password=get_password_hash("Tech123!"), department_id=dept_it.id, is_active=True
    )
    user_tech.roles.append(role_tech)

    user_emp = User(
        email="john.employee@company.com", username="john.employee", full_name="John Doe (Employee)",
        hashed_password=get_password_hash("User123!"), department_id=dept_eng.id, is_active=True
    )
    user_emp.roles.append(role_emp)

    user_sec = User(
        email="elena.sec@company.com", username="elena.sec", full_name="Elena Vance (Sec Analyst)",
        hashed_password=get_password_hash("Security123!"), department_id=dept_sec.id, is_active=True
    )
    user_sec.roles.append(role_sec)

    user_auditor = User(
        email="marcus.audit@company.com", username="marcus.audit", full_name="Marcus Vance (Auditor)",
        hashed_password=get_password_hash("Auditor123!"), department_id=dept_fin.id, is_active=True
    )
    user_auditor.roles.append(role_auditor)

    db.add_all([user_admin, user_mgr, user_tech, user_emp, user_sec, user_auditor])
    db.flush()

    # 4. IT Services
    srv_vpn = ITService(name="Global VPN Gateway", description="Secure remote access concentrator for enterprise workforce", tier=ServiceTier.MISSION_CRITICAL.value, status=ServiceStatus.OPERATIONAL.value, owner_name="Sarah Jenkins")
    srv_auth = ITService(name="Okta Identity & SSO", description="Single sign-on, MFA, and directory federation", tier=ServiceTier.MISSION_CRITICAL.value, status=ServiceStatus.OPERATIONAL.value, owner_name="Elena Vance")
    srv_erp = ITService(name="SAP S/4HANA ERP", description="Core accounting and corporate financial ledger", tier=ServiceTier.BUSINESS_CRITICAL.value, status=ServiceStatus.OPERATIONAL.value, owner_name="Robert Miller")
    srv_mail = ITService(name="Exchange Online & Outlook", description="Corporate messaging and shared calendar infrastructure", tier=ServiceTier.BUSINESS_CRITICAL.value, status=ServiceStatus.OPERATIONAL.value, owner_name="Sarah Jenkins")

    db.add_all([srv_vpn, srv_auth, srv_erp, srv_mail])
    db.flush()

    # 5. CMDB Assets
    asset_laptop1 = Asset(
        asset_tag="AST-MAC-0142", serial_number="C02G894HKMD6", manufacturer="Apple", model="MacBook Pro 16 M3 Max",
        asset_type=AssetType.LAPTOP.value, department_id=dept_eng.id, assigned_user_id=user_emp.id,
        purchase_date=now - timedelta(days=180), warranty_expiration=now + timedelta(days=550),
        status=AssetStatus.ACTIVE.value, location="Building A - Floor 4 (Eng Wing)",
        specifications="Apple M3 Max 16-Core CPU, 64GB Unified Memory, 2TB PCIe Gen4 SSD"
    )
    asset_server1 = Asset(
        asset_tag="AST-SRV-0089", serial_number="SN-DL380-9941A", manufacturer="HPE", model="ProLiant DL380 Gen10",
        asset_type=AssetType.SERVER.value, department_id=dept_it.id, assigned_user_id=user_admin.id,
        purchase_date=now - timedelta(days=400), warranty_expiration=now + timedelta(days=695),
        status=AssetStatus.ACTIVE.value, location="Datacenter North - Rack 12",
        specifications="Dual Intel Xeon Gold 6248R 24C, 256GB ECC RAM, 8x 3.84TB SAS SSD in RAID 10"
    )
    asset_router = Asset(
        asset_tag="AST-NET-0021", serial_number="FOC24190ABC", manufacturer="Cisco", model="Catalyst 9300-48P",
        asset_type=AssetType.SWITCH.value, department_id=dept_it.id, assigned_user_id=user_admin.id,
        purchase_date=now - timedelta(days=700), warranty_expiration=now + timedelta(days=20), # Expiring soon for demo!
        status=AssetStatus.ACTIVE.value, location="Building A - MDF Telecom Closet",
        specifications="48-port PoE+, 4x 10G SFP+ Uplinks, Network Essentials License"
    )

    db.add_all([asset_laptop1, asset_server1, asset_router])
    db.flush()

    # 6. SLA Policies
    sla_crit = SLAPolicy(name="Mission Critical SLA", priority=PriorityLevel.CRITICAL.value, target_response_mins=15, target_resolution_mins=120, business_hours_only=False, is_active=True)
    sla_high = SLAPolicy(name="High Priority SLA", priority=PriorityLevel.HIGH.value, target_response_mins=60, target_resolution_mins=480, business_hours_only=True, is_active=True)
    sla_med = SLAPolicy(name="Medium Standard SLA", priority=PriorityLevel.MEDIUM.value, target_response_mins=240, target_resolution_mins=1440, business_hours_only=True, is_active=True)
    sla_low = SLAPolicy(name="Low Request SLA", priority=PriorityLevel.LOW.value, target_response_mins=480, target_resolution_mins=4320, business_hours_only=True, is_active=True)

    db.add_all([sla_crit, sla_high, sla_med, sla_low])
    db.flush()

    # 7. Tickets
    t1 = Ticket(
        reference_number="TIK-2026-0001",
        subject="Remote VPN authentication timing out on London gateway",
        description="Unable to establish IPSec tunnel when connecting from home Wi-Fi. Client reports handshake error 809.",
        requester_id=user_emp.id,
        assigned_technician_id=user_tech.id,
        department_id=dept_eng.id,
        related_asset_id=asset_laptop1.id,
        category="Network",
        impact=ImpactLevel.HIGH.value,
        urgency=UrgencyLevel.CRITICAL.value,
        priority=PriorityLevel.CRITICAL.value,
        status=TicketStatus.IN_PROGRESS.value,
        created_at=now - timedelta(hours=3),
        response_deadline=now - timedelta(hours=2, minutes=45),
        resolution_deadline=now - timedelta(hours=1),
        first_responded_at=now - timedelta(hours=2, minutes=50)
    )

    t2 = Ticket(
        reference_number="TIK-2026-0002",
        subject="Request for Docker Desktop Enterprise license renewal",
        description="Local developer environment Docker subscription expired this morning, blocking container builds.",
        requester_id=user_emp.id,
        assigned_technician_id=user_tech.id,
        department_id=dept_eng.id,
        category="Software",
        impact=ImpactLevel.MEDIUM.value,
        urgency=UrgencyLevel.MEDIUM.value,
        priority=PriorityLevel.MEDIUM.value,
        status=TicketStatus.RESOLVED.value,
        created_at=now - timedelta(days=2),
        resolved_at=now - timedelta(days=1),
        first_responded_at=now - timedelta(days=2, hours=-1),
        resolution_details="Allocated seat from enterprise pool. Verified license activation key."
    )

    t3 = Ticket(
        reference_number="TIK-2026-0003",
        subject="Floor 3 network printer showing paper jam sensor error",
        description="LaserJet Enterprise M608 in HR hallway keeps reporting tray 2 jam even after physical inspection.",
        requester_id=user_emp.id,
        department_id=dept_hr.id,
        category="Hardware",
        impact=ImpactLevel.LOW.value,
        urgency=UrgencyLevel.MEDIUM.value,
        priority=PriorityLevel.LOW.value,
        status=TicketStatus.NEW.value,
        created_at=now - timedelta(minutes=45),
        response_deadline=now + timedelta(hours=7),
        resolution_deadline=now + timedelta(hours=71)
    )

    db.add_all([t1, t2, t3])
    db.flush()

    # Ticket SLA tracking
    track1 = SLATracking(ticket_id=t1.id, sla_policy_id=sla_crit.id, response_deadline=t1.response_deadline, resolution_deadline=t1.resolution_deadline, response_met=True, resolution_met=None)
    track2 = SLATracking(ticket_id=t2.id, sla_policy_id=sla_med.id, response_deadline=now - timedelta(days=2), resolution_deadline=now - timedelta(days=1), response_met=True, resolution_met=True)
    db.add_all([track1, track2])

    # Ticket comments & history
    c1 = TicketComment(ticket_id=t1.id, author_id=user_emp.id, comment_type=CommentType.PUBLIC.value, content="I tested both cellular hotspot and home fiber; both return error code 809.")
    c2 = TicketComment(ticket_id=t1.id, author_id=user_tech.id, comment_type=CommentType.INTERNAL_NOTE.value, content="Investigating radius server load on LDN-VPN-01. Noticed a spike in dropped packets.")
    c3 = TicketComment(ticket_id=t1.id, author_id=user_tech.id, comment_type=CommentType.PUBLIC.value, content="Hello John, our network engineering team has initiated diagnostic packet captures.")
    db.add_all([c1, c2, c3])

    # 8. Incidents & Major Incident (Module B)
    inc_major = Incident(
        incident_number="INC-2026-0001",
        title="MAJOR INCIDENT: Europe VPN Concentrator cluster failover degradation",
        description="A routing misconfiguration on border gateway protocol caused degraded throughput and authentication packet loss affecting 120+ remote workers.",
        is_major=True,
        affected_service="Global VPN Gateway",
        severity=IncidentSeverity.SEV1_CRITICAL.value,
        status=IncidentStatus.INVESTIGATING.value,
        incident_commander_id=user_mgr.id,
        reporter_id=user_tech.id,
        detected_at=now - timedelta(hours=3),
        root_cause="BGP route flapping triggered by upstream Tier-1 carrier maintenance without prior advisory."
    )
    inc_major.linked_tickets.append(t1)
    db.add(inc_major)
    db.flush()

    # Problem record & Known error
    prb = ProblemRecord(
        problem_number="PRB-2026-0001",
        title="Intermittent MTU fragmentation on IPSec over UDP 4500",
        description="Packets exceeding 1420 bytes are fragmented improperly by certain home ISP routers.",
        root_cause="Carrier MTU defaults vs IPsec encapsulation overhead.",
        workaround="Lower local MTU on client adapter to 1380.",
        status="UNDER_INVESTIGATION",
        owner_id=user_tech.id
    )
    ke = KnownError(
        error_code="ERR-VPN-809",
        title="VPN Connection Error 809 (NAT-T / Port 4500 blocked)",
        description="The network connection between your computer and the VPN server could not be established because the remote server is not responding.",
        symptoms="Client hangs at 'Connecting...' then times out with 809.",
        workaround="Add 'AssumeUDPEncapsulationContextOnSendRule' DWORD registry key set to 2 under HKLM\\SYSTEM\\CurrentControlSet\\Services\\PolicyAgent.",
        permanent_solution="Enable automated UDP NAT traversal on edge Palo Alto firewalls."
    )
    db.add_all([prb, ke])

    # 9. Change Management (Module D)
    chg = ChangeRequest(
        change_number="CHG-2026-0001",
        title="Upgrade Core Firewall Firmware to PAN-OS 11.1.2-h3",
        description="Apply critical security hotfix and BGP route stability patch across perimeter firewalls.",
        change_type=ChangeType.NORMAL.value,
        business_justification="Resolves high-severity CVE-2026-3401 and mitigates BGP flapping experienced during carrier maintenance.",
        affected_systems="Perimeter Palo Alto 5220 HA Pair (Primary & Secondary)",
        risk_level=ChangeRisk.HIGH.value,
        risk_assessment="High risk of transient packet loss (10-15s) during state synchronization failover.",
        implementation_plan="1. Verify secondary HA sync. 2. Install patch on secondary. 3. Initiate graceful peer failover. 4. Patch primary. 5. Failback and verify traffic.",
        test_procedure="Run synthetic ping probes and TCP health checks against all DMZ endpoints during maintenance window.",
        rollback_plan="Reboot to previous partition (PAN-OS 11.0.4) within 5 minutes if health check fails.",
        scheduled_start=now + timedelta(days=2, hours=2),
        scheduled_end=now + timedelta(days=2, hours=4),
        status=ChangeStatus.APPROVED.value,
        requester_id=user_tech.id,
        approved_by_id=user_mgr.id,
        approval_decision_at=now - timedelta(hours=6),
        approval_notes="Approved by CAB. Ensure network engineer standby on bridges."
    )
    db.add(chg)
    db.flush()

    chg_hist = ChangeHistory(
        change_request_id=chg.id,
        changed_by_id=user_mgr.id,
        action="APPROVED",
        details="Approved following review of rollback and failover telemetry."
    )
    db.add(chg_hist)

    # 10. Cybersecurity Operations (Module E)
    sec_inc = SecurityIncident(
        incident_number="SEC-2026-0001",
        title="Executive Impersonation Phishing Campaign targeting Finance Dept",
        description="Multiple employees in Finance received spear-phishing emails claiming to be from the CEO requesting urgent wire transfer authorization.",
        category=SecurityCategory.PHISHING.value,
        severity=SecuritySeverity.HIGH.value,
        status=SecurityStatus.INVESTIGATING.value,
        reporter_id=user_emp.id,
        assigned_analyst_id=user_sec.id,
        detected_at=now - timedelta(hours=5),
        containment_actions="Purged 14 malicious emails across Exchange mailboxes via Microsoft Graph API. Blocked sender domain 'corp-exec-urgent.com' at edge gateway."
    )
    db.add(sec_inc)
    db.flush()

    sec_tl = SecurityTimeline(
        security_incident_id=sec_inc.id,
        author_id=user_sec.id,
        action_type="CONTAINMENT",
        notes="Domain blocked at mail gateway. SIEM query executed to check if any user clicked embedded bit.ly shortlink."
    )
    sec_ev = SecurityEvidence(
        security_incident_id=sec_inc.id,
        evidence_type="Email Header & Raw EML",
        description="Headers show spoofed From field originating from bulletproof hosting IP 185.220.101.5 in Netherlands.",
        hash_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        added_by_id=user_sec.id
    )
    db.add_all([sec_tl, sec_ev])

    # 11. Knowledge Base (Module F)
    kb1 = KnowledgeArticle(
        title="Enterprise VPN Setup and Troubleshooting Guide",
        slug="enterprise-vpn-setup-and-troubleshooting-guide",
        content="### Overview\nAll remote staff must use GlobalProtect with Okta Verify Push MFA.\n\n### Troubleshooting Common Errors\n- **Error 809:** Check firewall or router UDP port 4500.\n- **Error 500:** Stale session tokens. Clear application cache under Settings > Connection.\n- **DNS Leak Test:** Verify corporate intranet DNS resolves `portal.corp.local`.",
        category="Network",
        tags="vpn,remote,network,security",
        author_id=user_tech.id,
        status=ArticleStatus.PUBLISHED.value,
        published_at=now - timedelta(days=14),
        view_count=324,
        helpful_count=48,
        not_helpful_count=2
    )
    kb2 = KnowledgeArticle(
        title="How to Request Software Licenses and Cloud Access",
        slug="how-to-request-software-licenses-and-cloud-access",
        content="### Software Procurement Workflow\n1. Search the Service Catalog for approved software.\n2. Submit a request through the Service Desk with your manager's cost-center approval.\n3. IT will provision license keys within 4 business hours.",
        category="Software",
        tags="license,software,procurement",
        author_id=user_mgr.id,
        status=ArticleStatus.PUBLISHED.value,
        published_at=now - timedelta(days=20),
        view_count=189,
        helpful_count=31,
        not_helpful_count=1
    )
    db.add_all([kb1, kb2])

    # 12. Monitoring Devices & Telemetry (Module H)
    dev1 = MonitoringDevice(name="Core-Switch-01", device_type="SWITCH", ip_address="10.0.0.1", hostname="sw01.core.corp.local", is_active=True, last_heartbeat=now)
    dev2 = MonitoringDevice(name="Prod-DB-Cluster-01", device_type="DATABASE", ip_address="10.0.2.15", hostname="pg01.db.corp.local", is_active=True, last_heartbeat=now)
    dev3 = MonitoringDevice(name="App-Server-Web01", device_type="SERVER", ip_address="10.0.3.50", hostname="web01.app.corp.local", is_active=True, last_heartbeat=now)
    db.add_all([dev1, dev2, dev3])
    db.flush()

    # Add historical metric records
    for i in range(10):
        t_offset = now - timedelta(minutes=i * 5)
        m1 = MonitoringMetric(device_id=dev1.id, cpu_percent=22.4 + i*0.5, memory_percent=45.1, disk_percent=38.0, ping_ms=1.2, service_health="HEALTHY", created_at=t_offset)
        m2 = MonitoringMetric(device_id=dev2.id, cpu_percent=78.2 + (i%3)*4.1, memory_percent=86.4, disk_percent=68.2, ping_ms=2.4, service_health="HEALTHY", created_at=t_offset)
        m3 = MonitoringMetric(device_id=dev3.id, cpu_percent=41.0, memory_percent=55.0, disk_percent=51.2, ping_ms=3.1, service_health="HEALTHY", created_at=t_offset)
        db.add_all([m1, m2, m3])

    # 13. Automation Rules (Module I)
    rule1 = AutomationRule(
        name="Critical Ticket IT Manager Notification",
        description="Notify the IT Operations Manager immediately when a Critical priority ticket is submitted.",
        trigger_event=TriggerEvent.ON_TICKET_CREATED.value,
        conditions_json='{"priority": "CRITICAL"}',
        actions_json='[{"type": "NOTIFY_ROLE", "role": "it_manager", "title": "CRITICAL TICKET ALERT", "message": "A P1 critical ticket was submitted and requires immediate oversight."}]',
        is_active=True,
        execution_count=1
    )
    rule2 = AutomationRule(
        name="Employee Confirmation Request on Ticket Resolution",
        description="Send notification to employee when ticket is marked RESOLVED to confirm issue closure.",
        trigger_event=TriggerEvent.ON_TICKET_RESOLVED.value,
        conditions_json='{}',
        actions_json='[{"type": "NOTIFY_USER", "title": "Ticket Resolved", "message": "Your IT ticket has been marked resolved. Please confirm resolution or reopen within 48h."}]',
        is_active=True,
        execution_count=3
    )
    db.add_all([rule1, rule2])

    # 14. Initial Audit Log
    audit_init = AuditLog(
        user_id=user_admin.id,
        username=user_admin.username,
        action="SYSTEM_INITIALIZATION",
        entity_type="SYSTEM",
        entity_id="1",
        ip_address="127.0.0.1",
        user_agent="System Bootstrap CLI",
        new_values='{"status": "READY", "version": "1.0.0"}'
    )
    db.add(audit_init)

    db.commit()
    print("Seed data successfully inserted.")
