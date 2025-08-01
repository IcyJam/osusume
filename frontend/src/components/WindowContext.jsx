import { createContext, useContext, useState, useRef } from "react";

const WindowContext = createContext();

export function WindowProvider({ children }) {
    const [focusedWindowId, setFocusedWindowId] = useState(null);                       // Stores the reference to the currently focused window
    const [zIndexMap, setZIndexMap] = useState({});                                     // Stores the zIndexes of all windows
    const zIndexCounter = useRef(100);                                                  // Max zIndex, incremented when a window takes focus

    const bringToFront = (id) => {
        zIndexCounter.current += 1;                                                     // Increments the max zIndex
        setZIndexMap((prev) => {
            const newMap = { ...prev, [id]: zIndexCounter.current };                    // Updates the zIndex of the current window in the map
            return newMap;
        });
        setFocusedWindowId(id);                                                         // Sets the focused window as the current one
    };

    return (                                                                            // Context that needs to wrap the whole app so that every child can access the focus-related information
        <WindowContext.Provider value={{ focusedWindowId, bringToFront, zIndexMap }}>
            {children}
        </WindowContext.Provider>
    );
}

export function useWindowContext() {                                                    // Function that can be called by children to access the context
    const context = useContext(WindowContext);
    if (!context) {
        throw new Error("useWindowContext must be used within a WindowProvider");
    }
    return context;
}