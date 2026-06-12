import { useEffect, useRef, useCallback } from 'react';

/**
 * Smooth count-up animation for numbers (scores, stats, etc.)
 * Usage: const ref = useCountUp(74, 1400); → <span ref={ref} />
 */
export function useCountUp(target, duration = 1400, round = true) {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let start = null;
    let raf;
    const step = (ts) => {
      if (!start) start = ts;
      const p = Math.min((ts - start) / duration, 1);
      // Cubic ease-out
      const v = p < 1 ? 1 - Math.pow(1 - p, 3) : 1;
      const val = round ? Math.round(v * target) : (v * target).toFixed(1);
      if (ref.current) ref.current.textContent = String(val);
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target, duration, round]);
  return ref;
}

/**
 * SVG ring/circle progress animation (for readiness ring)
 * Usage: const ref = useRingAnimation(score, circumference); → <circle ref={ref} />
 */
export function useRingAnimation(target, circumference, delay = 100) {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const offset = circumference - (circumference * target / 100);
    const timer = setTimeout(() => {
      if (ref.current) ref.current.style.strokeDashoffset = String(offset);
    }, delay);
    return () => clearTimeout(timer);
  }, [target, circumference, delay]);
  return ref;
}

/**
 * Scroll-triggered reveal animation — adds 'show' class when element enters viewport.
 * Requires CSS: .reveal { opacity:0; transform:translateY(12px); transition: opacity .55s, transform .55s; }
 *               .reveal.show { opacity:1; transform:none; }
 * Usage: const ref = useReveal(); → <div ref={ref} className="reveal">
 */
export function useReveal() {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    // Already visible? show immediately
    const rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight && rect.bottom > 0) {
      el.classList.add('show');
      return;
    }
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          e.target.classList.add('show');
          io.unobserve(e.target);
        }
      },
      { threshold: 0.1 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return ref;
}

/**
 * Lightweight toast notification (no library needed)
 * Usage: const showToast = useToast(); → showToast("সংরক্ষিত হয়েছে!");
 * Requires a <div id="toast" /> in the DOM (already in App.jsx layout)
 */
export function useToast() {
  const timerRef = useRef(null);
  const showToast = useCallback((msg) => {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => t.classList.remove('show'), 2500);
  }, []);
  return showToast;
}
