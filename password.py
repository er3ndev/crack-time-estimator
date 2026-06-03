#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Password Crack Time Estimator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Estimates how long it would take various organizations (FBI, NSA, GCHQ, etc.)
to brute-force a given password, based on real-world GPU hashcat benchmarks
and estimated institutional compute capacity.

Supports 10 hash algorithms and 13 attacker profiles including
a theoretical future quantum computer using Grover's algorithm.

Usage:
    python password.py

Author: eren
License: MIT
"""

import math
import string
import sys
import os
import random

# ══════════════════════════════════════════════════════════════
# TERMINAL COLORS
# ══════════════════════════════════════════════════════════════

class Colors:
    HEADER    = '\033[95m'
    BLUE      = '\033[94m'
    CYAN      = '\033[96m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    RED       = '\033[91m'
    BOLD      = '\033[1m'
    DIM       = '\033[2m'
    UNDERLINE = '\033[4m'
    RESET     = '\033[0m'
    MAGENTA   = '\033[35m'
    WHITE     = '\033[97m'
    BG_RED    = '\033[41m'
    BG_GREEN  = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE   = '\033[44m'

# enable ANSI escapes + UTF-8 on windows
if sys.platform == "win32":
    os.system("")
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# ══════════════════════════════════════════════════════════════
# HASH ALGORITHMS & REAL GPU BENCHMARKS
# ══════════════════════════════════════════════════════════════
# Source: hashcat benchmarks on a single NVIDIA RTX 4090 (2024/2025)

HASH_ALGORITHMS = {
    "MD5": {
        "description": "MD5 (Legacy, insecure)",
        "single_gpu_hps": 164.0e9,     # ~164 GH/s
        "security": "VERY WEAK",
    },
    "SHA-1": {
        "description": "SHA-1 (Deprecated)",
        "single_gpu_hps": 56.0e9,      # ~56 GH/s
        "security": "WEAK",
    },
    "SHA-256": {
        "description": "SHA-256 (Common)",
        "single_gpu_hps": 22.0e9,      # ~22 GH/s
        "security": "MODERATE",
    },
    "SHA-512": {
        "description": "SHA-512",
        "single_gpu_hps": 7.5e9,       # ~7.5 GH/s
        "security": "MODERATE",
    },
    "bcrypt (cost=10)": {
        "description": "bcrypt (Strong, slow hash)",
        "single_gpu_hps": 184.0e3,     # ~184 KH/s
        "security": "STRONG",
    },
    "bcrypt (cost=12)": {
        "description": "bcrypt (Very strong)",
        "single_gpu_hps": 46.0e3,      # ~46 KH/s
        "security": "VERY STRONG",
    },
    "scrypt": {
        "description": "scrypt (Memory-hard)",
        "single_gpu_hps": 3.2e6,       # ~3.2 MH/s
        "security": "STRONG",
    },
    "Argon2": {
        "description": "Argon2 (Modern, strongest)",
        "single_gpu_hps": 1.5e3,       # ~1.5 KH/s
        "security": "STRONGEST",
    },
    "NTLM": {
        "description": "NTLM (Windows passwords)",
        "single_gpu_hps": 300.0e9,     # ~300 GH/s
        "security": "VERY WEAK",
    },
    "WPA2": {
        "description": "WPA2 (Wi-Fi passwords)",
        "single_gpu_hps": 2.5e6,       # ~2.5 MH/s
        "security": "STRONG",
    },
}


# ══════════════════════════════════════════════════════════════
# ORGANIZATION PROFILES & ESTIMATED COMPUTE POWER
# ══════════════════════════════════════════════════════════════
# GPU counts are based on OSINT reports, budget analysis,
# and known supercomputer capabilities.

ORGANIZATIONS = {
    "🏠 Home User": {
        "description": "Single gaming GPU (RTX 4090)",
        "gpu_count": 1,
        "gpu_multiplier": 1.0,
        "country": "Individual",
    },
    "💻 Small Hacker Group": {
        "description": "8x RTX 4090 cracking rig",
        "gpu_count": 8,
        "gpu_multiplier": 1.0,
        "country": "Anonymous",
    },
    "🏢 Mid-size Company": {
        "description": "GPU cluster (50x A100)",
        "gpu_count": 50,
        "gpu_multiplier": 1.3,  # A100 is ~30% faster than 4090 for hashing
        "country": "Corporate",
    },
    "🇨🇦 RCMP (Canada)": {
        "description": "Royal Canadian Mounted Police - Cyber Crime Unit",
        "gpu_count": 200,
        "gpu_multiplier": 1.3,
        "country": "Canada",
    },
    "🇬🇧 GCHQ (UK)": {
        "description": "Government Communications HQ - SIGINT",
        "gpu_count": 5_000,
        "gpu_multiplier": 1.5,  # custom ASIC/FPGA acceleration
        "country": "United Kingdom",
    },
    "🇩🇪 BND (Germany)": {
        "description": "Bundesnachrichtendienst - Federal Intelligence",
        "gpu_count": 3_000,
        "gpu_multiplier": 1.4,
        "country": "Germany",
    },
    "🇮🇱 Unit 8200 (Israel)": {
        "description": "Israeli SIGINT National Unit",
        "gpu_count": 8_000,
        "gpu_multiplier": 1.5,
        "country": "Israel",
    },
    "🇷🇺 FSB (Russia)": {
        "description": "Federal Security Service - Cyber Operations",
        "gpu_count": 10_000,
        "gpu_multiplier": 1.4,
        "country": "Russia",
    },
    "🇨🇳 MSS (China)": {
        "description": "Ministry of State Security - Cyber Army",
        "gpu_count": 50_000,
        "gpu_multiplier": 1.3,  # Huawei Ascend GPUs
        "country": "China",
    },
    "🇺🇸 FBI (USA)": {
        "description": "Federal Bureau of Investigation - Regional Labs",
        "gpu_count": 15_000,
        "gpu_multiplier": 1.5,
        "country": "USA",
    },
    "🇺🇸 CIA (USA)": {
        "description": "Central Intelligence Agency",
        "gpu_count": 50_000,
        "gpu_multiplier": 1.6,
        "country": "USA",
    },
    "🇺🇸 NSA (USA)": {
        "description": "National Security Agency - World's largest cryptanalysis capacity",
        "gpu_count": 500_000,
        "gpu_multiplier": 2.0,  # custom ASICs + quantum-assisted systems
        "country": "USA",
    },
    "⚛️ Quantum Computer (~2035)": {
        "description": "Theoretical fault-tolerant quantum computer (Grover's algorithm)",
        "gpu_count": 1,
        "gpu_multiplier": 1.0,
        "country": "Future",
        "quantum": True,
    },
}


# ══════════════════════════════════════════════════════════════
# PASSWORD ANALYSIS
# ══════════════════════════════════════════════════════════════

def analyze_password(password: str) -> dict:
    """Analyze a password and compute its character space, entropy, and weaknesses."""

    analysis = {
        "length": len(password),
        "has_lower": False,
        "has_upper": False,
        "has_digit": False,
        "has_special": False,
        "has_space": False,
        "has_unicode": False,
        "charset_size": 0,
        "entropy": 0.0,
        "total_combinations": 0,
        "all_repeating": False,
        "common_pattern": False,
        "dictionary_risk": False,
    }

    common_patterns = [
        "123", "abc", "qwerty", "password", "letmein", "admin",
        "welcome", "monkey", "dragon", "master", "login",
        "123456", "654321", "111111", "iloveyou", "sunshine",
        "princess", "football", "shadow", "michael", "trustno1",
    ]

    for ch in password:
        if ch in string.ascii_lowercase:
            analysis["has_lower"] = True
        elif ch in string.ascii_uppercase:
            analysis["has_upper"] = True
        elif ch in string.digits:
            analysis["has_digit"] = True
        elif ch == ' ':
            analysis["has_space"] = True
        elif ch in string.punctuation:
            analysis["has_special"] = True
        elif ord(ch) > 127:
            analysis["has_unicode"] = True

    # calculate charset size
    charset = 0
    if analysis["has_lower"]:
        charset += 26
    if analysis["has_upper"]:
        charset += 26
    if analysis["has_digit"]:
        charset += 10
    if analysis["has_special"]:
        charset += 33
    if analysis["has_space"]:
        charset += 1
    if analysis["has_unicode"]:
        charset += 100

    analysis["charset_size"] = charset

    # total keyspace
    if charset > 0 and len(password) > 0:
        analysis["total_combinations"] = charset ** len(password)
        analysis["entropy"] = math.log2(charset ** len(password))

    # weakness checks
    if len(set(password)) == 1 and len(password) > 1:
        analysis["all_repeating"] = True

    pw_lower = password.lower()
    for pattern in common_patterns:
        if pattern in pw_lower:
            analysis["common_pattern"] = True
            break

    if len(password) <= 8 and pw_lower in common_patterns:
        analysis["dictionary_risk"] = True

    return analysis


def format_time(seconds: float) -> str:
    """Convert seconds to a human-readable duration string with color coding."""
    if seconds < 0.001:
        return f"{Colors.RED}{Colors.BOLD}INSTANT (< 1 ms){Colors.RESET}"
    if seconds < 1:
        return f"{Colors.RED}{Colors.BOLD}{seconds*1000:.2f} milliseconds{Colors.RESET}"
    if seconds < 60:
        return f"{Colors.RED}{Colors.BOLD}{seconds:.2f} seconds{Colors.RESET}"
    if seconds < 3600:
        return f"{Colors.RED}{Colors.BOLD}{seconds/60:.2f} minutes{Colors.RESET}"
    if seconds < 86400:
        return f"{Colors.YELLOW}{Colors.BOLD}{seconds/3600:.2f} hours{Colors.RESET}"
    if seconds < 86400 * 30:
        return f"{Colors.YELLOW}{Colors.BOLD}{seconds/86400:.2f} days{Colors.RESET}"
    if seconds < 86400 * 365:
        return f"{Colors.GREEN}{seconds/(86400*30):.2f} months{Colors.RESET}"
    if seconds < 86400 * 365 * 1000:
        return f"{Colors.GREEN}{Colors.BOLD}{seconds/(86400*365):.2f} years{Colors.RESET}"
    if seconds < 86400 * 365 * 1e6:
        return f"{Colors.CYAN}{Colors.BOLD}{seconds/(86400*365*1000):.2f} thousand years{Colors.RESET}"
    if seconds < 86400 * 365 * 1e9:
        return f"{Colors.CYAN}{Colors.BOLD}{seconds/(86400*365*1e6):.2f} million years{Colors.RESET}"
    if seconds < 86400 * 365 * 1e12:
        return f"{Colors.BLUE}{Colors.BOLD}{seconds/(86400*365*1e9):.2f} billion years{Colors.RESET}"
    if seconds < 86400 * 365 * 1e15:
        return f"{Colors.MAGENTA}{Colors.BOLD}{seconds/(86400*365*1e12):.2f} trillion years{Colors.RESET}"

    years = seconds / (86400 * 365)
    exp = int(math.log10(years))
    coeff = years / (10 ** exp)
    return f"{Colors.MAGENTA}{Colors.BOLD}{coeff:.2f} x 10^{exp} years{Colors.RESET}"


def get_strength_level(entropy: float) -> tuple:
    """Return strength label, color, and progress bar based on entropy bits."""
    if entropy < 28:
        return ("VERY WEAK", Colors.RED, "████░░░░░░░░░░░░░░░░")
    elif entropy < 36:
        return ("WEAK", Colors.RED, "██████░░░░░░░░░░░░░░")
    elif entropy < 50:
        return ("FAIR", Colors.YELLOW, "██████████░░░░░░░░░░")
    elif entropy < 65:
        return ("GOOD", Colors.GREEN, "██████████████░░░░░░")
    elif entropy < 80:
        return ("STRONG", Colors.CYAN, "████████████████░░░░")
    elif entropy < 100:
        return ("VERY STRONG", Colors.BLUE, "██████████████████░░")
    else:
        return ("EXCELLENT", Colors.MAGENTA, "████████████████████")


def calculate_crack_time(total_combinations: float, hash_alg: dict,
                         org: dict) -> float:
    """Calculate the estimated brute-force crack time in seconds."""

    if org.get("quantum"):
        # Grover's algorithm gives a square-root speedup
        # estimated quantum speed: 10^6 Grover iterations/sec (optimistic)
        quantum_speed = 1e6
        effective_combinations = math.sqrt(total_combinations)
        return effective_combinations / quantum_speed

    single_gpu_hps = hash_alg["single_gpu_hps"]
    total_hps = single_gpu_hps * org["gpu_count"] * org["gpu_multiplier"]

    if total_hps == 0:
        return float('inf')

    # on average you need to try half the keyspace
    return (total_combinations / 2) / total_hps


def format_hashrate(hps: float) -> str:
    """Format hash/sec into a readable string."""
    if hps >= 1e18:
        return f"{hps/1e18:.1f} EH/s"
    if hps >= 1e15:
        return f"{hps/1e15:.1f} PH/s"
    if hps >= 1e12:
        return f"{hps/1e12:.1f} TH/s"
    if hps >= 1e9:
        return f"{hps/1e9:.1f} GH/s"
    if hps >= 1e6:
        return f"{hps/1e6:.1f} MH/s"
    if hps >= 1e3:
        return f"{hps/1e3:.1f} KH/s"
    return f"{hps:.1f} H/s"


# ══════════════════════════════════════════════════════════════
# DISPLAY FUNCTIONS
# ══════════════════════════════════════════════════════════════

def print_banner():
    print(f"""
{Colors.CYAN}{Colors.BOLD}
    ██████╗  █████╗ ███████╗███████╗██╗    ██╗ ██████╗ ██████╗ ██████╗
    ██╔══██╗██╔══██╗██╔════╝██╔════╝██║    ██║██╔═══██╗██╔══██╗██╔══██╗
    ██████╔╝███████║███████╗███████╗██║ █╗ ██║██║   ██║██████╔╝██║  ██║
    ██╔═══╝ ██╔══██║╚════██║╚════██║██║███╗██║██║   ██║██╔══██╗██║  ██║
    ██║     ██║  ██║███████║███████║╚███╔███╔╝╚██████╔╝██║  ██║██████╔╝
    ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝ ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═════╝
    {Colors.YELLOW}CRACK TIME ESTIMATOR{Colors.RESET}
    {Colors.DIM}FBI · NSA · CIA · GCHQ · BND · FSB · MSS · RCMP · Unit 8200{Colors.RESET}
    {Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
    {Colors.DIM}Real GPU benchmarks + Estimated institutional capacity{Colors.RESET}
""")


def print_analysis(analysis: dict, password: str):
    """Print the password analysis section."""
    level, color, bar = get_strength_level(analysis["entropy"])

    print(f"\n{Colors.BOLD}{'=' * 62}{Colors.RESET}")
    print(f"{Colors.BOLD}  📊 PASSWORD ANALYSIS{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 62}{Colors.RESET}")

    # mask the password for display
    if len(password) > 2:
        masked = password[0] + '*' * (len(password) - 2) + password[-1]
    else:
        masked = '*' * len(password)

    print(f"  Password (masked) : {Colors.BOLD}{masked}{Colors.RESET}")
    print(f"  Length            : {Colors.BOLD}{analysis['length']}{Colors.RESET} characters")
    print(f"  Charset size      : {Colors.BOLD}{analysis['charset_size']}{Colors.RESET} possible characters")

    if analysis["entropy"] > 0:
        print(f"  Entropy           : {Colors.BOLD}{analysis['entropy']:.2f} bits{Colors.RESET}")
    print(f"  Total keyspace    : {Colors.BOLD}{analysis['total_combinations']:.2e}{Colors.RESET}")
    print()

    # character types breakdown
    print(f"  {Colors.UNDERLINE}Character Types Used:{Colors.RESET}")
    types = [
        ("Lowercase (a-z)", analysis["has_lower"], "+26"),
        ("Uppercase (A-Z)", analysis["has_upper"], "+26"),
        ("Digits (0-9)", analysis["has_digit"], "+10"),
        ("Special chars (!@#...)", analysis["has_special"], "+33"),
        ("Space", analysis["has_space"], "+1"),
        ("Unicode/Emoji", analysis["has_unicode"], "+100"),
    ]
    for name, present, bonus in types:
        icon = f"{Colors.GREEN}✓{Colors.RESET}" if present else f"{Colors.DIM}✗{Colors.RESET}"
        bonus_str = f" {Colors.CYAN}({bonus}){Colors.RESET}" if present else ""
        print(f"    {icon} {name}{bonus_str}")

    print()
    print(f"  {Colors.UNDERLINE}Strength Level:{Colors.RESET}")
    print(f"    {color}{Colors.BOLD}[{bar}] {level}{Colors.RESET}")
    print(f"    {Colors.DIM}Entropy: {analysis['entropy']:.1f} bits{Colors.RESET}")

    # warnings
    warnings = []
    if analysis["all_repeating"]:
        warnings.append("⚠️  All characters are identical! Can be cracked instantly.")
    if analysis["common_pattern"]:
        warnings.append("⚠️  Common pattern/word detected! Vulnerable to dictionary attacks.")
    if analysis["dictionary_risk"]:
        warnings.append("🚨 This password exists in common password lists! Will be cracked in seconds.")
    if analysis["length"] < 8:
        warnings.append("⚠️  Less than 8 characters! Minimum 12+ recommended.")
    if not analysis["has_special"]:
        warnings.append("💡 Adding special characters would significantly increase security.")

    if warnings:
        print(f"\n  {Colors.YELLOW}{Colors.BOLD}⚠️  WARNINGS:{Colors.RESET}")
        for w in warnings:
            print(f"    {Colors.YELLOW}{w}{Colors.RESET}")


def print_results(analysis: dict, selected_hash: str):
    """Calculate and display crack times for all organizations."""

    hash_alg = HASH_ALGORITHMS[selected_hash]
    total_comb = analysis["total_combinations"]

    if total_comb == 0:
        print(f"\n{Colors.RED}Password is empty or invalid!{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD}{'=' * 62}{Colors.RESET}")
    print(f"{Colors.BOLD}  ⏱️  CRACK TIME ESTIMATES{Colors.RESET}")
    print(f"{Colors.BOLD}  Hash Algorithm: {Colors.CYAN}{hash_alg['description']}{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 62}{Colors.RESET}")

    print(f"\n  {Colors.DIM}{'Organization':<35} {'Power':>12}  {'Time':>22}{Colors.RESET}")
    print(f"  {Colors.DIM}{'─' * 35} {'─' * 12}  {'─' * 22}{Colors.RESET}")

    for name, org in ORGANIZATIONS.items():
        if org.get("quantum"):
            power_str = "Grover's"
        else:
            total_hps = hash_alg["single_gpu_hps"] * org["gpu_count"] * org["gpu_multiplier"]
            power_str = format_hashrate(total_hps)

        crack_sec = calculate_crack_time(total_comb, hash_alg, org)
        time_str = format_time(crack_sec)

        print(f"  {name:<35} {Colors.DIM}{power_str:>12}{Colors.RESET}  {time_str}")

    # compare with the age of the universe
    universe_age_sec = 13.8e9 * 365.25 * 86400  # ~13.8 billion years
    nsa_time = calculate_crack_time(total_comb, hash_alg, ORGANIZATIONS["🇺🇸 NSA (USA)"])

    print(f"\n  {Colors.DIM}{'─' * 62}{Colors.RESET}")

    if nsa_time > universe_age_sec:
        ratio = nsa_time / universe_age_sec
        print(f"  {Colors.MAGENTA}{Colors.BOLD}🌌 Even the NSA would need {ratio:.1f}x the age of the")
        print(f"     universe to crack this password!{Colors.RESET}")
    elif nsa_time > 86400 * 365 * 100:
        print(f"  {Colors.GREEN}{Colors.BOLD}✅ This password would take the NSA centuries.{Colors.RESET}")
    elif nsa_time > 86400 * 365:
        print(f"  {Colors.YELLOW}{Colors.BOLD}⚠️  The NSA could crack this within years.{Colors.RESET}")
    elif nsa_time > 86400:
        print(f"  {Colors.RED}{Colors.BOLD}🚨 The NSA could crack this within days!{Colors.RESET}")
    else:
        print(f"  {Colors.BG_RED}{Colors.WHITE}{Colors.BOLD} 💀 The NSA could crack this almost instantly! CHANGE YOUR PASSWORD! {Colors.RESET}")


def print_all_algorithms_table(analysis: dict):
    """Show a comparison table of crack times across all hash algorithms (NSA)."""

    total_comb = analysis["total_combinations"]
    nsa = ORGANIZATIONS["🇺🇸 NSA (USA)"]

    print(f"\n{Colors.BOLD}{'=' * 62}{Colors.RESET}")
    print(f"{Colors.BOLD}  📋 ALL HASH ALGORITHMS - NSA Crack Times{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 62}{Colors.RESET}")

    print(f"\n  {Colors.DIM}{'Algorithm':<22} {'Security':<12} {'NSA Time':>24}{Colors.RESET}")
    print(f"  {Colors.DIM}{'─' * 22} {'─' * 12} {'─' * 24}{Colors.RESET}")

    for name, alg in HASH_ALGORITHMS.items():
        crack_sec = calculate_crack_time(total_comb, alg, nsa)
        time_str = format_time(crack_sec)
        security = alg["security"]

        if security in ("VERY WEAK",):
            s_color = Colors.RED
        elif security in ("WEAK",):
            s_color = Colors.YELLOW
        elif security in ("MODERATE",):
            s_color = Colors.YELLOW
        elif security in ("STRONG",):
            s_color = Colors.GREEN
        else:
            s_color = Colors.CYAN

        print(f"  {name:<22} {s_color}{security:<12}{Colors.RESET} {time_str}")


def print_recommendations(analysis: dict):
    """Print password improvement recommendations."""

    print(f"\n{Colors.BOLD}{'=' * 62}{Colors.RESET}")
    print(f"{Colors.BOLD}  💡 RECOMMENDATIONS{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 62}{Colors.RESET}")

    tips = []

    if analysis["length"] < 12:
        tips.append(
            f"📏 Make your password at least {Colors.BOLD}12 characters{Colors.RESET}. "
            f"Each extra character {Colors.BOLD}exponentially{Colors.RESET} increases security."
        )

    if analysis["length"] < 16:
        tips.append(
            f"📏 Ideal length: {Colors.BOLD}16+ characters{Colors.RESET}. "
            f"Consider using a passphrase."
        )

    if not analysis["has_upper"]:
        tips.append(
            f"🔠 Add {Colors.BOLD}uppercase letters{Colors.RESET} → increases charset by +26."
        )

    if not analysis["has_special"]:
        tips.append(
            f"🔣 Add {Colors.BOLD}special characters{Colors.RESET} (!@#$%^&*) → +33 to charset."
        )

    if not analysis["has_digit"]:
        tips.append(
            f"🔢 Add {Colors.BOLD}digits{Colors.RESET} → +10 to charset."
        )

    if analysis["all_repeating"]:
        tips.append(
            f"🔄 {Colors.RED}Don't use repeating characters!{Colors.RESET} Every char should be different."
        )

    tips.append(
        f"🔐 Prefer services that use strong hash algorithms (bcrypt, Argon2)."
    )
    tips.append(
        f"🛡️  Enable {Colors.BOLD}Two-Factor Authentication (2FA){Colors.RESET} — a password alone is never enough!"
    )
    tips.append(
        f"📦 Use a {Colors.BOLD}password manager{Colors.RESET} (Bitwarden, 1Password, KeePass)."
    )

    for i, tip in enumerate(tips, 1):
        print(f"\n  {i}. {tip}")

    # generate an example strong passphrase
    words = ["cloud", "tiger", "blue", "star", "forest", "castle", "ocean",
             "thunder", "steel", "wind", "fire", "silver", "crystal",
             "falcon", "storm", "ember", "lunar", "iron", "volt", "apex"]
    example = "-".join(random.sample(words, 4))
    example_analysis = analyze_password(example)

    print(f"\n  {Colors.BOLD}{'─' * 58}{Colors.RESET}")
    print(f"  {Colors.CYAN}Example strong passphrase:{Colors.RESET} {Colors.BOLD}{example}{Colors.RESET}")
    print(f"  {Colors.DIM}Entropy: {example_analysis['entropy']:.1f} bits | "
          f"Length: {example_analysis['length']} chars{Colors.RESET}")


def hash_selection_menu() -> str:
    """Display hash algorithm selection menu and return the user's choice."""
    print(f"\n{Colors.BOLD}  Select a hash algorithm:{Colors.RESET}")
    algorithms = list(HASH_ALGORITHMS.keys())

    for i, name in enumerate(algorithms, 1):
        alg = HASH_ALGORITHMS[name]
        security = alg["security"]

        if security in ("VERY WEAK",):
            s_color = Colors.RED
        elif security in ("WEAK",):
            s_color = Colors.YELLOW
        elif security in ("MODERATE",):
            s_color = Colors.YELLOW
        elif security in ("STRONG",):
            s_color = Colors.GREEN
        else:
            s_color = Colors.CYAN

        print(f"    {Colors.BOLD}{i:>2}.{Colors.RESET} {name:<22} "
              f"{s_color}[{security}]{Colors.RESET} "
              f"{Colors.DIM}Single GPU: {format_hashrate(alg['single_gpu_hps'])}{Colors.RESET}")

    print(f"    {Colors.BOLD} 0.{Colors.RESET} Calculate for all algorithms")

    while True:
        try:
            choice = input(f"\n  {Colors.CYAN}Your choice (0-{len(algorithms)}) [default: 0]: {Colors.RESET}").strip()
            if choice == "" or choice == "0":
                return "ALL"
            choice_int = int(choice)
            if 1 <= choice_int <= len(algorithms):
                return algorithms[choice_int - 1]
            print(f"  {Colors.RED}Invalid choice!{Colors.RESET}")
        except ValueError:
            print(f"  {Colors.RED}Please enter a number!{Colors.RESET}")


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    print_banner()

    print(f"  {Colors.BOLD}Enter your password (secure — nothing is stored or logged):{Colors.RESET}")

    try:
        import getpass
        password = getpass.getpass(f"  {Colors.CYAN}🔑 Password: {Colors.RESET}")
    except Exception:
        password = input(f"  {Colors.CYAN}🔑 Password: {Colors.RESET}")

    if not password:
        print(f"\n  {Colors.RED}Password cannot be empty!{Colors.RESET}")
        return

    # analyze
    analysis = analyze_password(password)
    print_analysis(analysis, password)

    # hash selection
    selected_hash = hash_selection_menu()

    if selected_hash == "ALL":
        print(f"\n{Colors.DIM}  ℹ️  Detailed view defaulting to SHA-256{Colors.RESET}")
        print_results(analysis, "SHA-256")
        print_all_algorithms_table(analysis)
    else:
        print_results(analysis, selected_hash)

    # recommendations
    print_recommendations(analysis)

    # methodology
    print(f"\n{Colors.BOLD}{'=' * 62}{Colors.RESET}")
    print(f"{Colors.BOLD}  📚 METHODOLOGY & SOURCES{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 62}{Colors.RESET}")
    print(f"""
  {Colors.DIM}• GPU hash rates: Hashcat benchmarks (NVIDIA RTX 4090, 2024)
  • Institutional GPU counts: OSINT reports, budget analyses
  • NSA capacity: Snowden documents & academic estimates
  • Quantum: Grover's algorithm with sqrt(N) speedup
  • Calculation: Brute-force (average N/2 attempts)
  • Real-world dictionary attacks can be significantly faster!

  ⚠️  These estimates assume pure brute-force only.
     Rainbow tables, dictionary attacks, and social engineering
     can yield results much faster.{Colors.RESET}
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {Colors.YELLOW}Interrupted.{Colors.RESET}\n")
    except Exception as e:
        print(f"\n  {Colors.RED}Error: {e}{Colors.RESET}\n")
