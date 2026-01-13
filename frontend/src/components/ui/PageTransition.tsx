import { motion } from "framer-motion";
import { useLocation } from "react-router-dom";

interface PageTransitionProps {
    children: React.ReactNode;
}

const variants = {
    initial: { opacity: 0, y: 20, scale: 0.98 },
    animate: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, y: -20, scale: 1.02 },
};

export const PageTransition = ({ children }: PageTransitionProps) => {
    const location = useLocation();

    return (
        <motion.div
            key={location.pathname}
            variants={variants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className="w-full h-full"
        >
            {children}
        </motion.div>
    );
};
