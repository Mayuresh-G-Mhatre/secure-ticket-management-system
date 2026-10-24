import os
import requests

BASE_URL = os.getenv('STMS_BASE_URL', 'http://127.0.0.1:5000').rstrip('/')
TIMEOUT = 10

CREDS = {
    'admin': (os.getenv('STMS_ADMIN_USERNAME'), os.getenv('STMS_ADMIN_PASSWORD')),
    'engineer': (os.getenv('STMS_ENGINEER_USERNAME'), os.getenv('STMS_ENGINEER_PASSWORD')),
    'manager': (os.getenv('STMS_MANAGER_USERNAME'), os.getenv('STMS_MANAGER_PASSWORD')),
    'customer': (os.getenv('STMS_CUSTOMER_USERNAME'), os.getenv('STMS_CUSTOMER_PASSWORD')),
}

ROUTES = {
    '/admin-dashboard': ['admin'],
    '/engineer-dashboard': ['engineer'],
    '/manager-dashboard': ['manager'],
    '/manager-reports': ['manager'],
    '/customer-dashboard': ['customer'],
    '/manage-users': ['admin'],
    '/reports': ['admin'],
    '/settings': ['admin'],
    '/archived-tickets': ['admin'],
    '/unassigned-tickets': ['admin'],
    '/create-ticket': ['admin', 'manager', 'customer'],
}

DASHBOARDS = {
    'admin': '/admin-dashboard',
    'engineer': '/engineer-dashboard',
    'manager': '/manager-dashboard',
    'customer': '/customer-dashboard',
}

passed = failed = skipped = 0


def show(kind, msg):
    global passed, failed, skipped
    if kind == 'PASS':
        passed += 1
        mark = '✓'
    elif kind == 'FAIL':
        failed += 1
        mark = '✗'
    else:
        skipped += 1
        mark = '-'
    print(f'[{kind:<4}] {mark} {msg}')


def is_login_redirect(response):
    if response.status_code not in (301, 302, 303, 307, 308):
        return False
    location = response.headers.get('Location', '')
    return (
        location in ('/', '/login')
        or location.endswith('/')
        or location.endswith('/login')
    )


def get(session, path):
    return session.get(
        BASE_URL + path,
        allow_redirects=False,
        timeout=TIMEOUT,
    )


def login(session, role):
    username, password = CREDS[role]

    if not username or not password:
        show('SKIP', f'{role}: credentials not configured')
        return False

    try:
        response = session.post(
            BASE_URL + '/login',
            data={
                'username': username,
                'password': password,
                'role': role,
            },
            allow_redirects=False,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        show('FAIL', f'{role} login request failed: {exc}')
        return False

    expected = DASHBOARDS[role]
    location = response.headers.get('Location', '')

    if response.status_code in (301, 302, 303, 307, 308) and expected in location:
        show('PASS', f'{role} login succeeded')
        return True

    show(
        'FAIL',
        f'{role} login failed: HTTP {response.status_code}, Location={location}',
    )
    return False


def main():
    print('=' * 68)
    print('STMS LOCAL SECURITY TESTER')
    print('=' * 68)
    print('Target:', BASE_URL)

    try:
        response = requests.get(
            BASE_URL + '/',
            allow_redirects=False,
            timeout=TIMEOUT,
        )
        show(
            'PASS' if response.status_code == 200 else 'FAIL',
            f"server / returned HTTP {response.status_code}",
        )
    except requests.RequestException as exc:
        show('FAIL', f'Cannot reach Flask: {exc}')
        print('Start it first with: python app.py')
        return

    print('\n--- 1. Logged-out protection ---')
    session = requests.Session()

    for path in ROUTES:
        try:
            response = get(session, path)
            if is_login_redirect(response):
                show('PASS', f'{path} blocked while logged out')
            else:
                show(
                    'FAIL',
                    f'{path} exposed while logged out: HTTP {response.status_code}',
                )
        except requests.RequestException as exc:
            show('FAIL', f'{path}: {exc}')

    print('\n--- 2. Role-based access + logout ---')

    for role in ('admin', 'engineer', 'manager', 'customer'):
        print(f'\n[{role.upper()}]')
        session = requests.Session()

        if not login(session, role):
            continue

        for path, allowed_roles in ROUTES.items():
            try:
                response = get(session, path)

                if role in allowed_roles:
                    if response.status_code == 200:
                        show('PASS', f'{role} allowed: {path}')
                    else:
                        show(
                            'FAIL',
                            f'{role} should access {path}, got HTTP {response.status_code}',
                        )
                else:
                    if response.status_code == 403 or is_login_redirect(response):
                        show('PASS', f'{role} denied: {path}')
                    else:
                        show(
                            'FAIL',
                            f'{role} improperly allowed: {path} '
                            f'(HTTP {response.status_code})',
                        )
            except requests.RequestException as exc:
                show('FAIL', f'{role} -> {path}: {exc}')

        try:
            response = session.get(
                BASE_URL + '/logout',
                allow_redirects=False,
                timeout=TIMEOUT,
            )

            if response.status_code in (301, 302, 303, 307, 308):
                show('PASS', f'{role} logout endpoint responded')
            else:
                show(
                    'FAIL',
                    f'{role} logout returned HTTP {response.status_code}',
                )

            response = get(session, DASHBOARDS[role])

            if is_login_redirect(response):
                show('PASS', f'{role} session invalidated after logout')
            else:
                show(
                    'FAIL',
                    f'{role} still accesses dashboard after logout',
                )
        except requests.RequestException as exc:
            show('FAIL', f'{role} logout test: {exc}')

    print('\n--- 3. Manual checks required ---')
    print('These routes need real IDs and are intentionally not modified by this script:')
    print('  /ticket/<ticket_id>')
    print('  /add-note/<ticket_id>')
    print('  /update-status/<ticket_id>')
    print('  /assign-ticket/<ticket_id>')
    print('  /archive-ticket/<ticket_id>')
    print('  /restore-ticket/<ticket_id>')
    print('  /notification/<notif_id>/<ticket_id>')
    print('Also manually test /uploads/<filename> while logged out.')
    print("For object-level authorization, try a customer opening another customer's ticket ID.")

    print('\n' + '=' * 68)
    print(f'SUMMARY: PASS={passed}  FAIL={failed}  SKIP={skipped}')
    print('=' * 68)

    if failed:
        print('Do NOT push/deploy until the failed tests are reviewed.')
    else:
        print('No automated test failed. Complete the manual checks before deployment.')


if __name__ == '__main__':
    main()
