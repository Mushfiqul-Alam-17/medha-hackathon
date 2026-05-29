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

export default function StudyNotes({ loading, notes, source, onDownload, lang }) {
  const empty = notes && !notes.slow?.length && !notes.confused?.length && !notes.danger?.length;

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
            {notes.slow?.map((n, i) => (
              <div className="card note-card" key={"s" + i} data-testid={`note-slow-${i}`}>
                <span className="note-badge nb-slow">{t("slowBadge", lang)}</span>
                <div className="note-topic">{n.topic}</div>
                {n.explanation && <NoteRow label={t("explanation", lang)}>{n.explanation}</NoteRow>}
                {n.memoryTrick && <NoteRow label={t("memoryTrick", lang)}>{n.memoryTrick}</NoteRow>}
                {n.trapQuestion && <div className="note-trap">{t("trapQ", lang)} {n.trapQuestion}</div>}
              </div>
            ))}

            {notes.confused?.map((n, i) => (
              <div className="card note-card" key={"c" + i} data-testid={`note-confused-${i}`}>
                <span className="note-badge nb-confused">{t("confusedBadge", lang)}</span>
                <div className="note-topic">{n.topic}</div>
                {n.comparisonTable?.length > 0 && (
                  <div className="cmp-table">
                    {n.comparisonTable.map((row, j) => (
                      <div className={`cmp-row ${j === 0 ? "correct" : ""}`} key={j}>
                        <div className="cmp-c concept">{row.concept}</div>
                        <div className="cmp-c">{row.description}</div>
                      </div>
                    ))}
                  </div>
                )}
                {n.memoryTrick && <NoteRow label={t("memoryTrick", lang)}>{n.memoryTrick}</NoteRow>}
                {n.trapQuestion && <div className="note-trap">{t("trapQ", lang)} {n.trapQuestion}</div>}
              </div>
            ))}

            {notes.danger?.map((n, i) => (
              <div className="card note-card" key={"d" + i} data-testid={`note-danger-${i}`}>
                <span className="note-badge nb-danger">{t("dangerBadge", lang)}</span>
                <div className="note-topic">{n.topic}</div>
                {n.explanation && <NoteRow label={t("explanation", lang)}>{n.explanation}</NoteRow>}
                {n.whyCorrect && <NoteRow label={t("whyCorrect", lang)}>{n.whyCorrect}</NoteRow>}
                {n.whyTricked && <NoteRow label={t("whyTricked", lang)}>{n.whyTricked}</NoteRow>}
                {n.trapQuestion && <div className="note-trap">{t("trapQ", lang)} {n.trapQuestion}</div>}
              </div>
            ))}

            {source && <div className="note-src">— {source === "ai" ? "✨ AI-generated · Powered by Google Gemini" : "MEDHA classifier notes"} —</div>}
          </>
        )}
      </div>
    </div>
  );
}
