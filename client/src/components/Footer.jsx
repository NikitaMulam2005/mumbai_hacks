import { section } from "framer-motion/client";

const Footer = () => {
    return ( 
        <section className="mt-16 pb-8">
            <footer className="text-center pt-8 border-t border-white/10">
            <div className="flex flex-col items-center gap-4">
                <div className="text-2xl font-bold tracking-tighter text-white opacity-70 hover:opacity-100 transition-opacity cursor-default">
                TRUTHPULSE
                </div>
                <p className="text-slate-400 text-sm">
                Built with <span className="text-red-400 animate-pulse">❤️</span> and ☕ at <span className="text-white font-semibold">MumbaiHacks 2025</span>
                </p>
                <p className="text-[10px] text-slate-400 mt-4">
                © 2025 TruthPulse Initiative. All rights reserved.
                </p>
            </div>
            </footer>
        </section>
     );
}
 
export default Footer;