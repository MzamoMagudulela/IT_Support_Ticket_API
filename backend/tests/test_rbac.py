def test_employee_cannot_create_departments(client, employee_token):
    headers = {"Authorization": f"Bearer {employee_token}"}
    res = client.post("/api/v1/departments", json={
        "name": "Unauthorized Department",
        "code": "UNAUTH"
    }, headers=headers)
    assert res.status_code == 403

def test_admin_can_create_departments(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.post("/api/v1/departments", json={
        "name": "Quality Assurance",
        "code": "QA-TEST",
        "description": "QA Engineering Department"
    }, headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Quality Assurance"

def test_manager_change_approval_permission(client, manager_token, employee_token):
    # Employee cannot approve change
    emp_headers = {"Authorization": f"Bearer {employee_token}"}
    mgr_headers = {"Authorization": f"Bearer {manager_token}"}

    res_emp = client.post("/api/v1/changes/1/approval", json={"decision": "APPROVED", "comments": "ok"}, headers=emp_headers)
    assert res_emp.status_code == 403

    # Manager can approve change
    res_mgr = client.post("/api/v1/changes/1/approval", json={"decision": "APPROVED", "comments": "CAB sign-off confirmed"}, headers=mgr_headers)
    assert res_mgr.status_code in [200, 404]
