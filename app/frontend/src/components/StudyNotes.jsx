import { Download } from "lucide-react";
import { t } from "../utils/lang";

function NoteRow({ label, children }) {
  return (
    <div className="note-row">
      <span className="note-lbl">{label}</span>
      <div className="note-val">{children}</div>
    </div>
  );
}

function ComparisonTable({ rows }) {
  if (!rows || rows.length === 0) return null;
  return (
    <div className="cmp-table-v2">
      {rows.map((row, j) => (
        <div className={`cmp-row-v2 ${row.isCorrect ? "correct" : "wrong"}`} key={j}>
          <div className="cmp-concept">{row.isCorrect ? "✓" : "✗"} {row.concept}</div>
          <div className="cmp-desc">{row.description}</div>
        </div>
      ))}
    </div>
  );
}

export default function StudyNotes({ loading, notes, source, onDownload, lang }) {
  const empty = notes && !notes.slow?.length && !notes.confused?.length && !notes.danger?.length;

  // Section counter for numbering
  let sectionNum = 0;

  return (
    <div className="view" data-testid="notes-view">
      <div className="wrap">
        <div className="section-head" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: 16 }}>
          <div>
            <span className="pill">{t("notesEyebrow", lang)}</span>
            <h2 style={{ marginTop: 16 }}>{t("notesTitle", lang)}</h2>
            <p>{t("notesSub", lang)}</p>
          </div>
          {notes && !empty && (
            <button className="btn btn-ghost" style={{ padding: "10px 18px", fontSize: 14 }}
              data-testid="download-notes" onClick={onDownload}><Download size={15} style={{ marginRight: 8, verticalAlign: "middle" }} />{t("download", lang)}</button>
          )}
        </div>

        {loading && (
          <div className="notes-loading" data-testid="notes-loading">
            <div className="pulse-ring" />
            <p style={{ color: "var(--text)" }}>{t("notesLoading1", lang)}</p>
            <p style={{ color: "var(--text-dim)", fontSize: 14 }}>{t("notesLoading2", lang)}</p>
          </div>
        )}

        {!loading && empty && (
          <div className="card" data-testid="notes-empty">
            <p style={{ color: "var(--text-dim)" }}>{t("notesEmpty", lang)}</p>
          </div>
        )}

        {!loading && notes && !empty && (
          <>
            {/* ── SLOW SECTIONS ── */}
            {notes.slow?.map((n, i) => {
              sectionNum++;
              return (
                <div className="card note-card" key={"s" + i} data-testid={`note-slow-${i}`}>
                  <span className="note-badge nb-slow">
                    {lang === "bn" ? `সেকশন ${sectionNum} — ধীর` : `Section ${sectionNum} — Slow`}
                  </span>
                  <div className="note-topic">{n.topic}</div>
                  {n.explanation && <NoteRow label={t("explanation", lang)}>{n.explanation}</NoteRow>}
                  {n.speedNote && (
                    <div className="note-speed-callout">
                      ⏱ {n.speedNote}
                    </div>
                  )}
                  {n.memoryTrick && (
                    <div className="note-memory-callout">
                      💡 {lang === "bn" ? "মনে রাখো:" : "Remember:"} <strong>{n.memoryTrick}</strong>
                    </div>
                  )}
                  {n.trapQuestion && <div className="note-trap">🪤 {t("trapQ", lang)} "{n.trapQuestion}"</div>}
                </div>
              );
            })}

            {/* ── CONFUSED SECTIONS ── */}
            {notes.confused?.map((n, i) => {
              sectionNum++;
              return (
                <div className="card note-card" key={"c" + i} data-testid={`note-confused-${i}`}>
                  <span className="note-badge nb-confused">
                    {lang === "bn" ? `সেকশন ${sectionNum} — কগনিটিভ কনফ্লিক্ট` : `Section ${sectionNum} — Cognitive Conflict`}
                  </span>
                  <div className="note-topic">{n.topic}</div>
                  {n.explanation && <NoteRow label={t("explanation", lang)}>{n.explanation}</NoteRow>}
                  <ComparisonTable rows={n.comparisonTable} />
                  {n.memoryTrick && (
                    <div className="note-memory-callout">
                      💡 {lang === "bn" ? "মনে রাখো:" : "Remember:"} <strong>{n.memoryTrick}</strong>
                    </div>
                  )}
                  {n.trapQuestion && <div className="note-trap">🪤 {t("trapQ", lang)} "{n.trapQuestion}"</div>}
                </div>
              );
            })}

            {/* ── DANGER SECTIONS ── */}
            {notes.danger?.map((n, i) => {
              sectionNum++;
              return (
                <div className="card note-card" key={"d" + i} data-testid={`note-danger-${i}`}>
                  <span className="note-badge nb-danger">
                    {lang === "bn" ? `সেকশন ${sectionNum} — Confidently Wrong` : `Section ${sectionNum} — Confidently Wrong`}
                  </span>
                  <div className="note-topic">{n.topic}</div>
                  {n.explanation && <NoteRow label={t("explanation", lang)}>{n.explanation}</NoteRow>}
                  {n.dangerNote && (
                    <div className="note-danger-callout">
                      ⚠️ {n.dangerNote}
                    </div>
                  )}
                  {n.whyCorrect && <NoteRow label={t("whyCorrect", lang)}>{n.whyCorrect}</NoteRow>}
                  {n.whyTricked && <NoteRow label={t("whyTricked", lang)}>{n.whyTricked}</NoteRow>}
                  {n.memoryTrick && (
                    <div className="note-memory-callout">
                      💡 {lang === "bn" ? "মনে রাখো:" : "Remember:"} <strong>{n.memoryTrick}</strong>
                    </div>
                  )}
                  {n.trapQuestion && <div className="note-trap">🪤 {t("trapQ", lang)} "{n.trapQuestion}"</div>}
                </div>
              );
            })}

            {source && (
              <div className="note-src">
                — {
                  source === "groq" ? "✨ AI-generated · Powered by Groq (Llama 3.3 70B)" :
                  source === "openrouter" ? "✨ AI-generated · Powered by OpenRouter (Gemma 4)" :
                  source === "gemini" ? "✨ AI-generated · Powered by Google Gemini" :
                  source === "fallback" ? "📚 MEDHA Behavioral Notes (Offline Mode)" :
                  "✨ AI-generated Study Notes"
                } —
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
