export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const APP_NAME = "CodePilot AI";
export const APP_TAGLINE = "Autonomous AST Static Analysis & AI Reasoning Platform";

export const NAVIGATION_ITEMS = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: "LayoutDashboard",
    description: "System overview, scores & streaks",
  },
  {
    title: "Review Code",
    href: "/review",
    icon: "Code2",
    description: "Monaco editor & real-time AST/AI review",
  },
  {
    title: "Upload Project",
    href: "/upload",
    icon: "UploadCloud",
    description: "Archive upload & batch scanning",
  },
  {
    title: "Review History",
    href: "/history",
    icon: "History",
    description: "Search, filter & compare past audits",
  },
  {
    title: "Analytics",
    href: "/analytics",
    icon: "BarChart3",
    description: "Quality trends & complexity heatmaps",
  },
  {
    title: "Documentation",
    href: "/documentation",
    icon: "FileText",
    description: "Generate READMEs, docstrings & tests",
  },
  {
    title: "Reports",
    href: "/reports",
    icon: "Files",
    description: "Download JSON, Markdown & HTML deliverables",
  },
  {
    title: "Monitoring",
    href: "/monitoring",
    icon: "Activity",
    description: "Real-time subsystem health & latency",
  },
  {
    title: "Settings",
    href: "/settings",
    icon: "Settings",
    description: "API keys, webhooks & system preferences",
  },
  {
    title: "Profile",
    href: "/profile",
    icon: "User",
    description: "Account details & security settings",
  },
];

export const SUPPORTED_LANGUAGES = [
  { id: "python", label: "Python", extension: ".py" },
  { id: "javascript", label: "JavaScript (Beta)", extension: ".js" },
  { id: "typescript", label: "TypeScript (Beta)", extension: ".ts" },
  { id: "go", label: "Go (Beta)", extension: ".go" },
];

export const SAMPLE_PYTHON_CODE = `import os
import hashlib

def authenticate_user(username: str, password_attempt: str, stored_hash: str) -> bool:
    """Validate credentials and log user authentication."""
    # Bug risk: standard equality comparison is vulnerable to timing attacks
    computed_hash = hashlib.sha256(password_attempt.encode()).hexdigest()
    if computed_hash == stored_hash:
        # Insecure primitive: raw command execution
        os.system(f"echo User {username} logged in at $(date)")
        return True
    return False

def calculate_discount(price: float, discount: float) -> float:
    """Calculate discounted item price with boundary validation."""
    if discount < 0 or discount > 1:
        raise ValueError("Discount must be between 0.0 and 1.0")
    return price * (1.0 - discount)
`;
