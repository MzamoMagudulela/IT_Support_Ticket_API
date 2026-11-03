import pytest
from app.models.incident import IncidentSeverity
from app.models.change import ChangeType, ChangeRisk

def test_incident_lifecycle_and_child_linking(client, manager_token, technician_token):
    mgr_headers = {"Authorization": f"Bearer {manager_token}"}
    tech_headers = {"Authorization": f"Bearer {technician_token}"}

    # 1. Manager creates a Major Incident
    inc_res = client.post("/api/v1/incidents", json={
        "title": "Primary Datacenter SAN Fibre Outage",
        "description": "Redundant fibre fabric disrupted, storage pools unreachable",
        "is_major": True,
        "affected_service": "Storage SAN",
        "severity": "SEV1_CRITICAL",
        "incident_commander_id": 2
    }, headers=mgr_headers)
    assert inc_res.status_code == 200
    major_inc = inc_res.json()
    assert major_inc["is_major"] is True
    parent_id = major_inc["id"]

    # 2. Technician reports a child incident linked to parent
    child_res = client.post("/api/v1/incidents", json={
        "title": "ERP Database Storage I/O Error",
        "description": "S/4HANA instance hung due to missing SAN volume",
        "is_major": False,
        "parent_incident_id": parent_id,
        "affected_service": "SAP ERP",
        "severity": "SEV2_HIGH"
    }, headers=tech_headers)
    assert child_res.status_code == 200
    assert child_res.json()["parent_incident_id"] == parent_id

    # 3. Technician updates status and records RCA
    update_res = client.patch(f"/api/v1/incidents/{parent_id}", json={
        "status": "RESOLVED",
        "root_cause": "Faulty transceivers on Core SAN switch B",
        "resolution_summary": "Replaced hot-pluggable optical modules and verified LUN multipath",
        "post_incident_report": "Schedule quarterly optical transceiver firmware audits"
    }, headers=tech_headers)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "RESOLVED"
    assert "Faulty transceivers" in update_res.json()["root_cause"]

def test_change_management_cab_workflow(client, technician_token, manager_token, employee_token):
    tech_headers = {"Authorization": f"Bearer {technician_token}"}
    mgr_headers = {"Authorization": f"Bearer {manager_token}"}
    emp_headers = {"Authorization": f"Bearer {employee_token}"}

    # 1. Technician submits Normal RFC
    rfc_payload = {
        "title": "Upgrade Core Switch Firmware to v16.4",
        "description": "Zero-day vulnerability patch on distribution switch stack",
        "change_type": "NORMAL",
        "business_justification": "Mitigate CVE-2026-1049 remote buffer overflow",
        "affected_systems": "SW-CORE-01, SW-CORE-02",
        "risk_level": "HIGH",
        "risk_assessment": "Potential 5-minute STP convergence failover",
        "implementation_plan": "1. Backup running-config\n2. Reload secondary switch\n3. Switchover core\n4. Reload primary",
        "test_procedure": "Ping gateway and run continuous synthetic trace",
        "rollback_plan": "Restore boot image to backup flash partition",
        "scheduled_start": "2026-11-10T02:00:00Z",
        "scheduled_end": "2026-11-10T04:00:00Z"
    }
    rfc_res = client.post("/api/v1/changes", json=rfc_payload, headers=tech_headers)
    assert rfc_res.status_code == 200
    change_id = rfc_res.json()["id"]
    assert rfc_res.json()["status"] == "SUBMITTED_FOR_APPROVAL"

    # 2. Employee cannot approve
    deny_res = client.post(f"/api/v1/changes/{change_id}/approval", json={
        "decision": "APPROVED",
        "comments": "Looks fine to me"
    }, headers=emp_headers)
    assert deny_res.status_code == 403

    # 3. Manager approves with CAB sign-off notes
    appr_res = client.post(f"/api/v1/changes/{change_id}/approval", json={
        "decision": "APPROVED",
        "comments": "Approved by CAB committee during Tuesday change advisory board"
    }, headers=mgr_headers)
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "APPROVED"
    assert "CAB committee" in appr_res.json()["approval_notes"]

def test_cmdb_asset_tracking(client, admin_token, technician_token):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Register new hardware asset
    asset_payload = {
        "asset_tag": "SRV-TEST-9921",
        "serial_number": "SN-DELL-R750-X981",
        "manufacturer": "Dell Technologies",
        "model": "PowerEdge R750",
        "asset_type": "SERVER",
        "department_id": 1,
        "location": "Datacenter Rack D-04",
        "purchase_cost": 8450.00
    }
    create_res = client.post("/api/v1/assets", json=asset_payload, headers=admin_headers)
    assert create_res.status_code == 200
    asset_id = create_res.json()["id"]

    # 2. Assign asset to employee
    assign_res = client.post(f"/api/v1/assets/{asset_id}/assign", json={
        "assigned_user_id": 4,
        "notes": "Assigned server host to John Doe for dev environment"
    }, headers=admin_headers)
    assert assign_res.status_code == 200
    assert assign_res.json()["assigned_user_id"] == 4

    # 3. List assets with filter
    list_res = client.get("/api/v1/assets?asset_type=SERVER", headers=admin_headers)
    assert list_res.status_code == 200
    assert any(a["asset_tag"] == "SRV-TEST-9921" for a in list_res.json())

def test_security_incident_reporting_and_evidence(client, security_token, employee_token, auditor_token):
    sec_headers = {"Authorization": f"Bearer {security_token}"}
    emp_headers = {"Authorization": f"Bearer {employee_token}"}
    audit_headers = {"Authorization": f"Bearer {auditor_token}"}

    # 1. Employee creates a phishing security incident
    sec_res = client.post("/api/v1/security/incidents", json={
        "title": "Spear Phishing Email Targeting Payroll Execs",
        "description": "Suspicious spoofed sender requesting wire transfer verification",
        "category": "PHISHING",
        "severity": "HIGH",
        "status": "NEW"
    }, headers=emp_headers)
    assert sec_res.status_code == 200
    sec_id = sec_res.json()["id"]

    # 2. Security Analyst attaches cryptographic evidence
    ev_res = client.post(f"/api/v1/security/incidents/{sec_id}/evidence", json={
        "evidence_type": "EML_HEADERS",
        "description": "Raw RFC822 email headers showing SPF/DKIM validation failures",
        "hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }, headers=sec_headers)
    assert ev_res.status_code == 200
    assert ev_res.json()["hash_sha256"] == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    # 3. Security Analyst applies containment actions
    update_res = client.patch(f"/api/v1/security/incidents/{sec_id}", json={
        "status": "CONTAINED",
        "containment_actions": "Quarantined malicious sender domain on perimeter mail gateway"
    }, headers=sec_headers)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "CONTAINED"

    # 4. Auditor inspects security dashboard (allowed)
    aud_res = client.get("/api/v1/security/dashboard", headers=audit_headers)
    assert aud_res.status_code == 200
    assert "total_security_incidents" in aud_res.json()

    # 5. Regular employee cannot access security dashboard
    emp_deny = client.get("/api/v1/security/dashboard", headers=emp_headers)
    assert emp_deny.status_code == 403

def test_infrastructure_monitoring_webhooks(client, admin_token):
    # 1. Test telemetry pulse
    pulse_res = client.post("/api/v1/monitoring/pulse")
    assert pulse_res.status_code == 200

    # 2. Test Prometheus Alertmanager webhook with critical alert
    prom_payload = {
        "status": "firing",
        "receiver": "itsm-webhook",
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "PostgresDeadlockSpike",
                    "severity": "CRITICAL",
                    "instance": "db-primary.prod:5432"
                },
                "annotations": {
                    "summary": "Database transaction deadlocks exceed 50/sec threshold"
                }
            }
        ]
    }
    prom_res = client.post("/api/v1/monitoring/webhook/prometheus", json=prom_payload)
    assert prom_res.status_code == 200
    assert prom_res.json()["processed_alerts"] == 1

    # 3. Test Zabbix webhook
    zabbix_payload = {
        "host": "ESXi-Host-03",
        "ip": "10.0.1.30",
        "trigger_name": "VMware Host High Memory Ballooning",
        "severity": "CRITICAL",
        "details": "RAM hypervisor swapping threshold breached 95%"
    }
    zab_res = client.post("/api/v1/monitoring/webhook/zabbix", json=zabbix_payload)
    assert zab_res.status_code == 200
    assert zab_res.json()["device"] == "ESXi-Host-03"

    # 4. Active alerts should reflect these triggers
    alerts_res = client.get("/api/v1/monitoring/alerts?status=ACTIVE")
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) > 0

def test_knowledge_base_workflow(client, technician_token, employee_token):
    tech_headers = {"Authorization": f"Bearer {technician_token}"}
    emp_headers = {"Authorization": f"Bearer {employee_token}"}

    # 1. Technician authors troubleshooting guide
    kb_payload = {
        "title": "Resolving Cisco AnyConnect Certificate Errors",
        "content": "Step 1: Open certmgr.msc\nStep 2: Check corporate root CA validity\nStep 3: Flush DNS cache with ipconfig /flushdns",
        "category": "Troubleshooting Guides",
        "tags": "vpn, anyconnect, certificate, network",
        "is_published": True
    }
    kb_res = client.post("/api/v1/knowledge", json=kb_payload, headers=tech_headers)
    assert kb_res.status_code == 200
    kb_id = kb_res.json()["id"]

    # 2. Employee searches KB
    search_res = client.get("/api/v1/knowledge?search=AnyConnect", headers=emp_headers)
    assert search_res.status_code == 200
    assert any(a["id"] == kb_id for a in search_res.json())

    # 3. Employee sends feedback for article
    vote_res = client.post(f"/api/v1/knowledge/{kb_id}/feedback", json={"is_helpful": True, "feedback_text": "Solved my VPN issue immediately!"}, headers=emp_headers)
    assert vote_res.status_code == 200
    assert "feedback" in vote_res.json()["message"].lower()

    # 4. View article directly increments view count and reveals helpful count
    get_res = client.get(f"/api/v1/knowledge/{kb_id}", headers=emp_headers)
    assert get_res.status_code == 200
    assert get_res.json()["helpful_count"] >= 1
    assert get_res.json()["view_count"] >= 1
