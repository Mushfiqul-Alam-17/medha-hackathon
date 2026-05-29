import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

const WORDS = ["Merit", "Excellence", "Dedication", "Hustle", "Achievement"];

export default function IntroAnimation({ onComplete }) {
  const [phase, setPhase] = useState(0); // 0 words, 1 medha, 2 done

  useEffect(() => {
    const t1 = setTimeout(() => setPhase(1), 2200);
    const t2 = setTimeout(() => setPhase(2), 4000);
    const t3 = setTimeout(() => onComplete && onComplete(), 4600);
    return () => { [t1, t2, t3].forEach(clearTimeout); };
  }, [onComplete]);

  return (
    <AnimatePresence>
      {phase < 2 && (
        <motion.div className="intro" exit={{ opacity: 0 }} transition={{ duration: 0.6 }} data-testid="intro-animation">
          {phase === 0 && (
            <div className="intro-words">
              {WORDS.map((w, i) => (
                <motion.span key={w} className="intro-word"
                  initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.28, duration: 0.5 }}>
                  <b>{w[0]}</b>{w.slice(1)}
                </motion.span>
              ))}
            </div>
          )}
          {phase === 1 && (
            <motion.div initial={{ opacity: 0, scale: 0.92 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6 }} style={{ textAlign: "center" }}>
              <div className="intro-medha">MEDH<span>A</span></div>
              <div className="intro-tag">Know how you think.</div>
            </motion.div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
