import { useState, useRef, useLayoutEffect} 	from "react";
import { useDraggable, useDndMonitor } 			from "@dnd-kit/core";
import { headerColorMap } 						from "../utils/header_colors";

export default function DraggableWindow({ id, children, label, buttonIcon, headerColor }) {		
	const [position, setPosition] = useState({ x: 100, y: -30 });					// Committed position, i.e. position before/after being dragged. The start position is slightly offset relative to the icon.
	const [isVisible, setIsVisible] = useState(false);								// Indicates if the window should be displayed

	const [origin, setOrigin] = useState("top left");								// Position of the icon center relative to the window
	const iconRef = useRef(null);													// Reference to the icon associated to the window
	const windowRef = useRef(null);													// Reference to the window

	useLayoutEffect(() => {															// Called after the DOM updates, but before the browser paints
		if (iconRef.current && windowRef.current) {
			const iconRect = iconRef.current.getBoundingClientRect();				// Gets the references to the icon and the window
			const winRect = windowRef.current.getBoundingClientRect();

			const originX = iconRect.left - winRect.left + iconRect.width / 2;		// Calculates the position of the center of the icon relative to the top left of the window
			const originY = iconRect.top - winRect.top + iconRect.height / 2;		
			setOrigin(`${originX}px ${originY}px`);									// Sets that position as the origin used for the scaling animation
		}
	}, [isVisible]);																// Condition to call useLayoutEffect > only run when isVisible becomes true

	return (
		<div>
			<div ref={iconRef} onDoubleClick={() => setIsVisible(true)}
				className="cursor-pointer w-20 h-20 mb-2"
			>
				<img src={buttonIcon} />
			</div>

				<div ref={windowRef} style={{transformOrigin: origin}}						// Sets the scaling animation (origin point + behavior)
					className={`
						
						transition-all duration-200 ease-[cubic-bezier(0.6, 0.05, 0.28, 0.9)]
						${isVisible ? "opacity-100 scale-100 pointer-events-auto" : "opacity-0 scale-50 pointer-events-none"}
					`}
				>

					<DraggableObject id={id} position={position} label={label} headerColor={headerColor} onClose={() => setIsVisible(false)}
						onDragEnd={(delta) => setPosition((p) => ({x: p.x + delta.x, y: p.y + delta.y,}))}
					>
						<div className="w-full">
							{children}
						</div>
					</DraggableObject>

				</div>
		</div>
	);
}

function DraggableObject({ id, position, label, headerColor, children, onClose, onDragEnd }) {
	const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({ id });				// Returns all the attributes necessary to make an object Draggable

	const headerColorClass = headerColorMap[headerColor] || "bg-gray-300";

	useDndMonitor({ 																						
		onDragEnd(event) {
			if (event.active.id === id && event.delta) {
				onDragEnd?.(event.delta);																	// Commit the position when drag ends
			}
		},
	});

	const style = {
		position: "absolute",
		top: position.y,																					// Real layout position from which the delta is calculated
		left: position.x,
		transform: `translate3d(${transform ? transform.x : 0}px, ${transform ? transform.y : 0}px, 0)`,	// Position defined relatively to parent, changes while dragging
		zIndex: isDragging ? 1000 : 1,																		// TODO : Takes the focus when being dragged, to change for multiple windows
		cursor: 'grab',
	};

	return ( 																								// TODO : Style to define according to the global theme (colors, padding...)
		<div ref={setNodeRef} {...attributes} style={style} className="rounded shadow-md bg-white border border-gray-300 absolute">
		{/* |_ The whole div becomes draggable by giving it the 'setNodeRef' and 'attributes' */}

			<div className={`flex ${headerColorClass} text-black rounded-t`}>
			{/* |_ Header of the window */}

				<div {...listeners} className="cursor-move flex-1 p-2">
				{/* |_ Only this part is draggable since it has 'listeners'*/}
					{label}
				</div>

				<button onClick={onClose} className="ml-auto font-bold text-black hover:text-red-800 pl-3 pr-3">
				{/* |_ Button to close the window, 'ml-auto' pushes it to the far right of the header */}
					✕
				</button>
			</div>

			<div className="p-4">
			{/* |_ Content to be displayed inside of the window */}
				{children}
			</div>
		</div>
	);
}