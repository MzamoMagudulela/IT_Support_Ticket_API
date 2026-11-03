def test_employee_ticket_isolation(client, employee_token, admin_token):
    # Employee creates a ticket
    emp_headers = {"Authorization": f"Bearer {employee_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    create_payload = {
        "subject": "Confidential HR Inquiry",
        "description": "Sensitive payroll inquiry for employee 4",
        "category": "Software",
        "impact": "LOW",
        "urgency": "LOW"
    }
    create_res = client.post("/api/v1/tickets", json=create_payload, headers=emp_headers)
    assert create_res.status_code == 200
    ticket_id = create_res.json()["id"]

    # Employee can view their own ticket
    view_res = client.get(f"/api/v1/tickets/{ticket_id}", headers=emp_headers)
    assert view_res.status_code == 200

    # Admin can view ticket
    admin_res = client.get(f"/api/v1/tickets/{ticket_id}", headers=admin_headers)
    assert admin_res.status_code == 200

def test_priority_matrix_calculation(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "subject": "Critical Outage Test",
        "description": "High impact high urgency system failure",
        "category": "Infrastructure",
        "impact": "CRITICAL",
        "urgency": "CRITICAL"
    }
    res = client.post("/api/v1/tickets", json=payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["priority"] == "CRITICAL"

def test_ticket_status_lifecycle_and_assignment(client, admin_token, technician_token):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Create
    t_res = client.post("/api/v1/tickets", json={
        "subject": "Lifecycle Test Ticket",
        "description": "Testing status flow",
        "category": "Network",
        "impact": "MEDIUM",
        "urgency": "MEDIUM"
    }, headers=admin_headers)
    tid = t_res.json()["id"]

    # 2. Assign
    assign_res = client.post(f"/api/v1/tickets/{tid}/assign", json={
        "technician_id": 3,
        "reason": "Assigned to Alex for network check"
    }, headers=admin_headers)
    assert assign_res.status_code == 200
    assert assign_res.json()["assigned_technician_id"] == 3

    # 3. In Progress
    status_res = client.post(f"/api/v1/tickets/{tid}/status", json={
        "new_status": "IN_PROGRESS",
        "comment": "Beginning diagnostic work"
    }, headers=admin_headers)
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "IN_PROGRESS"

    # 4. Resolve
    resolve_res = client.post(f"/api/v1/tickets/{tid}/status", json={
        "new_status": "RESOLVED",
        "resolution_details": "Replaced bad SFP module"
    }, headers=admin_headers)
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"
    assert resolve_res.json()["resolved_at"] is not None
