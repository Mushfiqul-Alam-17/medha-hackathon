import Hero from "./Landing/Hero";
import Features from "./Landing/Features";
import ClassifierBreakdown from "./Landing/ClassifierBreakdown";
import HowItWorks from "./Landing/HowItWorks";
import Footer from "./Landing/Footer";

export default function Landing({ onStart, onDemo, lang }) {
  return (
    <div className="min-h-screen bg-[#FCF7F0] overflow-hidden" data-testid="landing-view">
      {/* Texture Background */}
      <div 
        className="fixed inset-0 pointer-events-none z-0 opacity-[0.018] mix-blend-multiply"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`
        }}
      />
      
      {/* Decorative Blobs */}
      <div className="absolute top-[-10%] right-[-5%] w-[60vw] h-[60vw] rounded-full bg-gradient-to-br from-[#F9E5DA] to-transparent blur-3xl opacity-60 mix-blend-multiply pointer-events-none z-0" />
      <div className="absolute top-[20%] left-[-10%] w-[40vw] h-[40vw] rounded-full bg-gradient-to-br from-[#E3EDE8] to-transparent blur-3xl opacity-50 mix-blend-multiply pointer-events-none z-0" />

      <div className="max-w-[1100px] mx-auto px-6 relative z-10">
        <Hero onStart={onStart} onDemo={onDemo} lang={lang} />
        <Features lang={lang} />
        <ClassifierBreakdown lang={lang} />
        <HowItWorks lang={lang} />
        <Footer lang={lang} />
      </div>
    </div>
  );
}
