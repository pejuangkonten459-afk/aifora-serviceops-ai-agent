def classify_request(title: str, description: str) -> dict:
    text = f"{title} {description}".lower()

    rules = [
        ("maintenance", [
            "maintenance", "perawatan", "perbaikan",
            "rusak", "kerusakan", "servis"
        ]),
        ("access", [
            "akses", "access", "akun", "password",
            "kata sandi", "login", "izin masuk"
        ]),
        ("equipment", [
            "perangkat", "equipment", "komputer",
            "laptop", "printer", "alat"
        ]),
    ]

    category = "general"
    for label, keywords in rules:
        if any(keyword in text for keyword in keywords):
            category = label
            break

    urgent_words = [
        "darurat", "emergency", "kritis", "critical",
        "tidak berfungsi", "berhenti beroperasi"
    ]
    priority = (
        "high"
        if any(word in text for word in urgent_words)
        else "normal"
    )

    return {
        "category": category,
        "priority": priority,
        "method": "keyword_rules",
    }
