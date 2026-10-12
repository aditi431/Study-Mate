import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import NotesSection from "./components/NotesSection";
import Footer from "./components/Footer";
import AboutPage from "./components/AboutPage";
import AskAIPage from "./components/AskAIPage";
import { useEffect, useState } from "react";
import { clearToken, getStoredToken } from "./lib/api";

const validPages = ["home", "notes", "ask-ai", "about"];

function getPageFromLocation() {
    const page = window.location.hash.slice(1);
    return validPages.includes(page) ? page : "home";
}

function App() {
    const [page, setPage] = useState(getPageFromLocation);
    const [showForm, setShowForm] = useState(false);
    const [token, setToken] = useState(() => getStoredToken());

    function signOut() {
        clearToken();
        setToken(null);
        setShowForm(false);
    }

    useEffect(() => {
        function expireSession() {
            setToken(null);
            setShowForm(false);
        }

        function scrollToCurrentPage() {
            const nextPage = getPageFromLocation();
            setPage(nextPage);
            document.getElementById(nextPage)?.scrollIntoView({ behavior: "smooth" });
        }

        function updateActivePage() {
            const activationLine = Math.max(110, window.innerHeight * 0.35);
            const visibleSections = validPages
                .map((id) => document.getElementById(id))
                .filter((section) => section && section.getBoundingClientRect().top <= activationLine);
            const activePage = visibleSections[visibleSections.length - 1];

            if (activePage) {
                setPage(activePage.id);
            }
        }

        window.addEventListener("popstate", scrollToCurrentPage);
        window.addEventListener("hashchange", scrollToCurrentPage);
        window.addEventListener("scroll", updateActivePage, { passive: true });
        window.addEventListener("studymate:auth-expired", expireSession);

        if (window.location.hash) {
            window.requestAnimationFrame(scrollToCurrentPage);
        }

        return () => {
            window.removeEventListener("popstate", scrollToCurrentPage);
            window.removeEventListener("hashchange", scrollToCurrentPage);
            window.removeEventListener("scroll", updateActivePage);
            window.removeEventListener("studymate:auth-expired", expireSession);
        };
    }, []);

    function navigateTo(nextPage) {
        if (!validPages.includes(nextPage)) {
            return;
        }

        if (window.location.hash !== `#${nextPage}`) {
            window.history.pushState({}, "", `#${nextPage}`);
        }
        setPage(nextPage);
        document.getElementById(nextPage)?.scrollIntoView({ behavior: "smooth" });
    }

    function openNoteForm() {
        setShowForm(true);
        navigateTo("notes");
    }

    return (
        <div className="app-shell">
            <Navbar page={page} onNavigate={navigateTo} />
            <Hero
                onAddNoteClick={openNoteForm}
                onNavigate={navigateTo}
            />
            <NotesSection
                showForm={showForm}
                onCloseForm={() => setShowForm(false)}
                token={token}
                onAuthenticated={setToken}
                onSignOut={signOut}
            />
            <AskAIPage token={token} />
            <AboutPage onNavigate={navigateTo} />
            <Footer onNavigate={navigateTo} />
        </div>
    );
}

export default App;