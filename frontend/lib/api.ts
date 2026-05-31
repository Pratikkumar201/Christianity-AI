// API client for the Christianity AI backend

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: string[];
  sources?: Source[];
  route?: string;
  routingConfidence?: number;
  confidence?: number;
  safety?: SafetyResult;
  validation?: ValidationResult;
  pipelineLog?: PipelineStage[];
  imageUrl?: string;
  responseTimeMs?: number;
  denomination?: string;
}

export interface Source {
  reference: string;
  text: string;
  score?: number;
}

export interface SafetyResult {
  allowed: boolean;
  risk_level: "low" | "medium" | "high";
  reason: string;
}

export interface ValidationResult {
  verified: boolean;
  citations: string[];
  issues: ValidationIssue[];
  hallucinated: string[];
  total_citations: number;
  valid_count: number;
}

export interface ValidationIssue {
  citation: string;
  reason: string;
  severity?: string;
}

export interface PipelineStage {
  stage: string;
  timestamp: number;
  [key: string]: unknown;
}

export interface VerseVerification {
  valid: boolean;
  book: string;
  chapter: number;
  verse: number;
  reason?: string;
  message: string;
}

export interface SessionInfo {
  session_id: string;
  denomination: string;
  message_count: number;
  history_length: number;
  created_at: string;
  last_active: string;
}

export interface EvaluationMetrics {
  fake_verse_detection_rate: number;
  real_verse_accuracy: number;
  safety_block_rate: number;
  safety_allow_rate: number;
  hallucination_prevention_rate: number;
  overall_score: number;
  total_tests: number;
  total_passed: number;
  eval_time_ms: number;
  results: Record<string, EvalSuiteResult>;
}

export interface EvalSuiteResult {
  test: string;
  passed: number;
  total: number;
  accuracy: number;
  details: EvalDetail[];
}

export interface EvalDetail {
  id?: string;
  input?: string;
  reference?: string;
  category?: string;
  expected?: string;
  got?: string;
  passed: boolean;
  reason?: string;
  risk_level?: string;
}

// ── API Functions ──────────────────────────────────────────────────────────────

export async function sendChat(
  message: string,
  sessionId: string,
  denomination: string
): Promise<ChatMessage> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId, denomination }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Chat API error: ${res.status} ${err}`);
  }

  const data = await res.json();

  return {
    role: "assistant",
    content: data.answer,
    citations: data.citations || [],
    sources: data.sources || [],
    route: data.route,
    routingConfidence: data.routing_confidence,
    confidence: data.confidence,
    safety: data.safety,
    validation: data.validation,
    pipelineLog: data.pipeline_log,
    imageUrl: data.image_url,
    responseTimeMs: data.response_time_ms,
    denomination: data.denomination,
  };
}

export async function generateImage(prompt: string, sessionId: string): Promise<{
  success: boolean;
  image_url: string | null;
  enhanced_prompt: string | null;
  answer: string;
  reason?: string;
}> {
  const res = await fetch(`${API_BASE}/image`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, session_id: sessionId }),
  });
  if (!res.ok) throw new Error(`Image API error: ${res.status}`);
  return res.json();
}

export async function verifyVerse(
  book: string,
  chapter: number,
  verse: number
): Promise<VerseVerification> {
  const res = await fetch(`${API_BASE}/verify-verse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ book, chapter, verse }),
  });
  if (!res.ok) throw new Error(`Verify API error: ${res.status}`);
  return res.json();
}

export async function getSessionInfo(sessionId: string): Promise<SessionInfo> {
  const res = await fetch(`${API_BASE}/session/${sessionId}`);
  if (!res.ok) throw new Error("Session fetch failed");
  return res.json();
}

export async function setDenomination(sessionId: string, denomination: string): Promise<void> {
  await fetch(`${API_BASE}/session/denomination`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, denomination }),
  });
}

export async function runEvaluation(): Promise<EvaluationMetrics> {
  const res = await fetch(`${API_BASE}/evaluation/run`);
  if (!res.ok) throw new Error("Evaluation failed");
  return res.json();
}

export async function getMetrics(): Promise<EvaluationMetrics> {
  const res = await fetch(`${API_BASE}/evaluation/metrics`);
  if (!res.ok) throw new Error("Metrics fetch failed");
  return res.json();
}

export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    return res.ok;
  } catch {
    return false;
  }
}

// ── Utilities ──────────────────────────────────────────────────────────────────

export function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

export const DENOMINATIONS = [
  "Non-denominational",
  "Catholic",
  "Protestant",
  "Orthodox",
  "Baptist",
  "Methodist",
  "Lutheran",
  "Pentecostal",
  "Anglican",
  "Presbyterian",
];

export const ROUTE_LABELS: Record<string, string> = {
  SCRIPTURE_QA: "Scripture Q&A",
  THEOLOGY_DISCUSSION: "Theology",
  CONTENT_GENERATION: "Content Gen",
  IMAGE_GENERATION: "Image Gen",
  VERSE_VERIFICATION: "Verse Check",
  SAFETY_VIOLATION: "Safety Block",
  GENERAL_CHAT: "General Chat",
};

export const ROUTE_ICONS: Record<string, string> = {
  SCRIPTURE_QA: "📖",
  THEOLOGY_DISCUSSION: "⛪",
  CONTENT_GENERATION: "✍️",
  IMAGE_GENERATION: "🎨",
  VERSE_VERIFICATION: "🔍",
  SAFETY_VIOLATION: "🛡️",
  GENERAL_CHAT: "💬",
};
