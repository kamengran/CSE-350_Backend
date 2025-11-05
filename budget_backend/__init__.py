from flask import Flask, request, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  # Allow access from frontend

    # ------------------------------------------------
    # 1️⃣ Route: Check server status
    # ------------------------------------------------
    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    # ------------------------------------------------
    # 2️⃣ Route: Calculate Financial Aid
    # ------------------------------------------------
    @app.route("/calc/financial_aid", methods=["POST"])
    def calc_financial_aid():
        data = request.get_json(force=True) or {}
        coa = float(data.get("costOfAttendance", 0))
        grants = float(data.get("grants", 0))
        scholarships = float(data.get("scholarships", 0))
        work_study = float(data.get("workStudy", 0))
        efc = float(data.get("efc", 0))

        gift_aid = grants + scholarships
        remaining_need = max(coa - gift_aid - work_study - efc, 0)

        subsidized = min(remaining_need, 3500)
        unsubsidized = max(remaining_need - subsidized, 0)

        return jsonify({
            "costOfAttendance": coa,
            "efc": efc,
            "giftAid": gift_aid,
            "remainingNeed": remaining_need,
            "suggestedLoans": {
                "subsidized": subsidized,
                "unsubsidized": unsubsidized
            },
            "workStudy": work_study
        })

    # ------------------------------------------------
    # 3️⃣ Route: Calculate Budget Buckets
    # ------------------------------------------------
    @app.route("/calc/buckets", methods=["POST"])
    def calc_buckets():
        data = request.get_json(force=True) or {}
        income = float(data.get("monthlyIncome", 0))

        ratios = {
            "Rent": 0.35,
            "Food": 0.10,
            "Transport": 0.08,
            "Utilities": 0.07,
            "Health": 0.05,
            "Savings": 0.15,
            "Entertainment": 0.08,
            "Other": 0.012,
        }

        plan = {k: round(income * v, 2) for k, v in ratios.items()}

        return jsonify({
            "income": income,
            "buckets": plan
        })

    # ------------------------------------------------
    # 4️⃣ Route: Calculate Savings Plan
    # ------------------------------------------------
    @app.route("/calc/savings", methods=["POST"])
    def calc_savings():
        data = request.get_json(force=True) or {}
        goal = float(data.get("goal", 0))
        months = int(data.get("months", 1))
        apy = float(data.get("apy", 0)) / 100

        # simple monthly compound interest
        monthly_rate = apy / 12
        monthly_deposit = goal / months
        projected_balance = monthly_deposit * (((1 + monthly_rate) ** months - 1) / monthly_rate) if monthly_rate else goal

        return jsonify({
            "goal": goal,
            "months": months,
            "apy": apy * 100,
            "monthlyDeposit": round(monthly_deposit, 2),
            "projectedBalance": round(projected_balance, 2)
        })

    # ------------------------------------------------
    # 5️⃣ Route: Compare Spending to Budget
    # ------------------------------------------------
    @app.route("/calc/compare", methods=["POST"])
    def calc_compare():
        """
        Compare user's spending in a specific category against the recommended goal.
        Example request:
        {
            "monthlyIncome": 2000,
            "category": "Food",
            "items": [
                {"name": "groceries", "cost": 50},
                {"name": "snacks", "cost": 10}
            ]
        }
        """
        data = request.get_json(force=True) or {}
        income = float(data.get("monthlyIncome", 0))
        category = data.get("category", "Food")
        items = data.get("items", [])

        # Budget ratios from calc_buckets
        ratios = {
            "Rent": 0.35, "Food": 0.10, "Transport": 0.08, "Utilities": 0.07,
            "Health": 0.05, "Savings": 0.15, "Entertainment": 0.08, "Other": 0.012
        }

        goal = income * ratios.get(category, 0.05)
        spent = sum(float(x.get("cost", 0)) for x in items)
        remaining = goal - spent

        return jsonify({
            "category": category,
            "goal": round(goal, 2),
            "spent": round(spent, 2),
            "remaining": round(remaining, 2),
            "status": "ok" if remaining >= 0 else "over budget"
        })

    return app
