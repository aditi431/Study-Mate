import { useState } from "react";

const links = [
    { id: "home",    label: "Home"     },
    { id: "notes",   label: "My Notes" },
    { id: "ask-ai",  label: "Ask AI"   },
    { id: "about",   label: "About"    },
];

function Navbar({ page, onNavigate }) {
    const [menuOpen, setMenuOpen] = useState(false);

    const handleNav = (id) => {
        onNavigate(id);
        setMenuOpen(false);
    };

    return (
        <header className="navbar nav-image">

            {/* Logo */}
            <a
                className="brand nav-brand"
                href="#home"
                aria-label="StudyMate home"
                onClick={(e) => { e.preventDefault(); handleNav("home"); }}
            >
                <span className="nav-brand__name">StudyMate</span>
            </a>

            {/* Center links — desktop */}
            <nav className="nav-center" aria-label="Main navigation">
                {links.map((link) => (
                    <a
                        key={link.id}
                        href={`#${link.id}`}
                        className={`nav-link${page === link.id ? " nav-link--active" : ""}`}
                        aria-current={page === link.id ? "page" : undefined}
                        onClick={(e) => { e.preventDefault(); handleNav(link.id); }}
                    >
                        {link.label}
                    </a>
                ))}
            </nav>

            {/* Right actions */}
            <div className="nav-actions">
                <button className="nav-icon-btn" aria-label="Messages" type="button">
                    <svg width="19" height="19" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" strokeWidth="2"
                        strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                    </svg>
                </button>
                <button className="nav-icon-btn" aria-label="Notifications" type="button">
                    <svg width="19" height="19" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" strokeWidth="2"
                        strokeLinecap="round" strokeLinejoin="round">
                        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                        <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                    </svg>
                </button>
                <button
                    className={`nav-hamburger${menuOpen ? " nav-hamburger--open" : ""}`}
                    aria-label="Toggle menu"
                    aria-expanded={menuOpen}
                    type="button"
                    onClick={() => setMenuOpen((v) => !v)}
                >
                    <span />
                    <span />
                    <span />
                </button>
            </div>

            {/* Mobile drawer */}
            {menuOpen && (
                <div className="nav-drawer" role="menu">
                    {links.map((link) => (
                        <a
                            key={link.id}
                            href={`#${link.id}`}
                            className={`nav-drawer__link${page === link.id ? " nav-drawer__link--active" : ""}`}
                            role="menuitem"
                            onClick={(e) => { e.preventDefault(); handleNav(link.id); }}
                        >
                            {link.label}
                        </a>
                    ))}
                </div>
            )}
        </header>
    );
}

export default Navbar;