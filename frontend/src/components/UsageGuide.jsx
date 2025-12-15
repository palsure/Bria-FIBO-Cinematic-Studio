import React, { useEffect, useRef } from 'react';

const UsageGuide = ({ isOpen, onClose }) => {
    const modalRef = useRef(null);

    useEffect(() => {
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                onClose();
            }
        };

        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
            // Prevent body scrolling when modal is open
            document.body.style.overflow = 'hidden';
        }

        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.body.style.overflow = 'unset';
        };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div
                className="modal-content usage-guide-modal"
                onClick={e => e.stopPropagation()}
                ref={modalRef}
                role="dialog"
                aria-modal="true"
                aria-labelledby="usage-guide-title"
            >
                <div className="modal-header">
                    <h2 id="usage-guide-title">🎬 FIBO Studio Usage Guide</h2>
                    <button className="close-button" onClick={onClose} aria-label="Close guide">
                        &times;
                    </button>
                </div>

                <div className="modal-body">
                    <section>
                        <h3>✨ Creating a Storyboard</h3>
                        <ol>
                            <li>
                                <strong>Step 1: Scripting</strong>
                                <ul>
                                    <li>Paste your script text directly into the text area</li>
                                    <li>OR click <em>"Upload Script File"</em> to use a text file</li>
                                    <li>The storyboard generates automatically after parsing</li>
                                </ul>
                            </li>
                            <li>
                                <strong>Step 2: Scene Generation and Editing</strong>
                                <ul>
                                    <li>Review the AI-generated scenes</li>
                                    <li>Click <strong>"✏️ Edit Scene"</strong> to customize a scene</li>
                                    <li>Adjust camera angles, lighting, color, and composition</li>
                                    <li>Click <em>"Apply Changes"</em> to regenerate with new settings</li>
                                </ul>
                            </li>
                            <li>
                                <strong>Step 3: Save Your Work</strong>
                                <ul>
                                    <li>Enter a storyboard name and click <em>"Save Storyboard"</em></li>
                                    <li>Individual scenes can be saved to "My Scenes"</li>
                                </ul>
                            </li>
                        </ol>
                    </section>

                    <section>
                        <h3>📚 Managing Your Work</h3>
                        <ul>
                            <li><strong>My Storyboards:</strong> View, load, edit, or delete saved storyboards</li>
                            <li><strong>My Scenes:</strong> Manage individual saved scenes and their parameters</li>
                        </ul>
                    </section>

                    <section>
                        <h3>📤 Export Options</h3>
                        <ul>
                            <li><strong>Export PDF:</strong> Generate professional storyboard documents</li>
                            <li><strong>Export Animatic:</strong> Create a video sequence from your storyboard</li>
                        </ul>
                    </section>
                </div>

                <div className="modal-footer">
                    <button className="primary-button" onClick={onClose}>Got it</button>
                </div>
            </div>
        </div>
    );
};

export default UsageGuide;
