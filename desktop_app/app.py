import flet as ft
import requests
import base64

API_URL = "http://127.0.0.1:8000"

def main(page: ft.Page):
    page.title = "Eco Action Tracker"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    username_field = ft.TextField(label="Username", width=300)
    password_field = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
    message_text = ft.Text(value="", color="red")

    user_points = ft.Text(value="Total Points: 0", size=16, color="green")
    current_user = {"username": None}

    # --- Backend Calls ---
    def register_user(e):
        res = requests.post(f"{API_URL}/auth/register", json={
            "username": username_field.value.strip(),
            "password": password_field.value.strip()
        })
        if res.status_code == 200:
            message_text.value = "✅ Registration successful!"
            message_text.color = "green"
        else:
            message_text.value = f"❌ {res.json().get('detail', 'Error')}"
            message_text.color = "red"
        page.update()

    def login_user(e):
        res = requests.post(f"{API_URL}/auth/login", json={
            "username": username_field.value.strip(),
            "password": password_field.value.strip()
        })
        if res.status_code == 200:
            message_text.value = f"✅ Welcome, {username_field.value}!"
            message_text.color = "green"
            current_user["username"] = username_field.value
            show_dashboard()
        else:
            message_text.value = f"❌ {res.json().get('detail', 'Invalid credentials')}"
            message_text.color = "red"
        page.update()

    def log_action(action_name, quantity):
        res = requests.post(f"{API_URL}/actions/log", json={
            "username": current_user["username"],
            "action_name": action_name,
            "quantity": quantity
        })
        if res.status_code == 200:
            data = res.json()
            user_points.value = f"Total Points: {data['points']}"
            message_text.value = f"✅ Logged: {action_name} × {quantity}"
            message_text.color = "green"
        else:
            message_text.value = "❌ Failed to log action."
            message_text.color = "red"
        page.update()

    # --- Dialog for Quantity ---
    def open_quantity_dialog(action_name, label_text):
        qty_field = ft.TextField(label=label_text, width=200, autofocus=True)

        def close_dialog(e):
            dialog.open = False
            page.update()

        def submit_dialog(e):
            try:
                qty = float(qty_field.value or 0)
            except ValueError:
                qty = 0
            dialog.open = False
            page.update()
            if qty > 0:
                log_action(action_name, qty)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Log {action_name}"),
            content=qty_field,
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Submit", on_click=submit_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    # --- Leaderboard ---
    def show_leaderboard(e=None):
        res = requests.get(f"{API_URL}/leaderboard")
        if res.status_code != 200:
            message_text.value = "❌ Could not fetch leaderboard"
            message_text.color = "red"
            page.update()
            return

        data = res.json()
        leaderboard_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Rank")),
                ft.DataColumn(ft.Text("Username")),
                ft.DataColumn(ft.Text("Points"))
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(i+1))),
                        ft.DataCell(ft.Text(user["username"])),
                        ft.DataCell(ft.Text(str(user["points"])))
                    ]
                )
                for i, user in enumerate(data)
            ]
        )

        page.clean()
        page.add(
            ft.Text("🏆 Leaderboard", size=24, weight=ft.FontWeight.BOLD),
            leaderboard_table,
            ft.ElevatedButton("Back", on_click=lambda e: show_dashboard())
        )

    # --- Stats (chart) ---
    def show_stats(e=None):
        if not current_user["username"]:
            message_text.value = "❌ Please log in to view stats"
            message_text.color = "red"
            page.update()
            return

        res = requests.get(f"{API_URL}/stats/user/{current_user['username']}/chart")
        if res.status_code != 200:
            message_text.value = f"❌ Could not fetch stats: {res.status_code}"
            message_text.color = "red"
            page.update()
            return

        # Convert image bytes to base64 for Flet Image
        img_b64 = base64.b64encode(res.content).decode("ascii")
        img = ft.Image(src_base64=img_b64, width=800, height=400)

        page.clean()
        page.add(
            ft.Text("📈 Your Stats", size=24, weight=ft.FontWeight.BOLD),
            img,
            ft.Row([
                ft.ElevatedButton("Back", on_click=lambda e: show_dashboard())
            ], alignment=ft.MainAxisAlignment.CENTER)
        )

    # --- Challenges ---
    def show_challenges(e=None):
        if not current_user["username"]:
            message_text.value = "❌ Please log in to view challenges"
            message_text.color = "red"
            page.update()
            return

        res = requests.get(f"{API_URL}/challenges", params={"username": current_user["username"]})
        if res.status_code != 200:
            # show server response detail when available
            try:
                detail = res.json()
            except Exception:
                detail = res.text
            message_text.value = f"❌ Could not fetch challenges: {detail}"
            message_text.color = "red"
            page.update()
            return

        data = res.json()
        challenges_list = []

        for ch in data:
            progress = ch.get("progress", 0)
            goal = ch.get("goal", 1)
            done = progress >= goal
            challenges_list.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(ch["title"], size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(ch.get("description", "")),
                            ft.ProgressBar(value=min(progress/goal, 1.0), width=250),
                            ft.Text(f"{progress}/{goal} completed"),
                            ft.Text("✅ Completed!" if done else "", color="green")
                        ]
                    ),
                    bgcolor="#1E1E1E",
                    padding=10,
                    border_radius=10,
                )
            )

        page.clean()
        page.add(
            ft.Text("🌿 Eco Challenges", size=24, weight=ft.FontWeight.BOLD),
            *challenges_list,
            ft.ElevatedButton("Back", on_click=lambda e: show_dashboard())
        )

    # --- Dashboard ---
    def show_dashboard():
        page.clean()
        page.add(
            ft.Text(f"Welcome, {current_user['username']}", size=20),
            user_points,
            ft.Text("Select an action:", size=16),
            ft.ElevatedButton("🚲 Ride a Bike", on_click=lambda e: open_quantity_dialog("Rode a Bike", "How many kilometers?")),
            ft.ElevatedButton("🌳 Plant a Tree", on_click=lambda e: open_quantity_dialog("Planted a Tree", "How many trees?")),
            ft.ElevatedButton("🛍 Use Reusable Bags", on_click=lambda e: open_quantity_dialog("Used a Reusable Bag", "How many bags?")),
            ft.ElevatedButton("♻ Recycle Plastic", on_click=lambda e: open_quantity_dialog("Recycled Plastic", "How many plastics?")),
            ft.Row([
                ft.ElevatedButton("🏆 View Leaderboard", on_click=show_leaderboard),
                ft.ElevatedButton("📈 View Stats", on_click=show_stats),
                ft.ElevatedButton("🏁 Challenges", on_click=show_challenges),
                ft.ElevatedButton("🚪 Logout", on_click=lambda e: show_login())
            ], alignment=ft.MainAxisAlignment.CENTER),
            message_text
        )

    # --- Login Page ---
    def show_login():
        page.clean()
        page.add(
            ft.Text("Eco Action Tracker", size=25, weight=ft.FontWeight.BOLD),
            username_field,
            password_field,
            ft.Row([
                ft.ElevatedButton("Login", on_click=login_user),
                ft.ElevatedButton("Register", on_click=register_user)
            ], alignment=ft.MainAxisAlignment.CENTER),
            message_text
        )

    show_login()

ft.app(target=main)