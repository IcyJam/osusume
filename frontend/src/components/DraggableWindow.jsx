import { useState, useRef } from "react";
import { DndContext, useDraggable } from "@dnd-kit/core";
import { restrictToWindowEdges } from "@dnd-kit/modifiers";

export default function DraggableWindow({ id, children, label }) {
	const [position, setPosition] = useState({ x: 100, y: 100 });					// Committed position, i.e. position before/after being dragged
	const [isVisible, setIsVisible] = useState(false);								// Indicates if the window should be displayed
	const [origin, setOrigin] = useState("top left");								// Position of the icon center relative to the window
	const iconRef = useRef(null);													// Reference to the icon associated to the window
	const windowRef = useRef(null);													// Reference to the window

	return (
		<div>
			<div ref={iconRef} onDoubleClick={() => setIsVisible(true)}
				className="cursor-pointer w-16 h-16 bg-blue-200 rounded flex items-center justify-center shadow-md absolute left-8 top-8"
			></div>
			<DndContext																	// Context that wraps around the draggable element
				modifiers={[restrictToWindowEdges]}										// Makes it so that the draggable window can't go over the screen's borders
				onDragEnd={({ delta }) => {												// Called when the user stops dragging
				setPosition((p) => ({ x: p.x + delta.x, y: p.y + delta.y }));			// Adds the last drag delta to the committed coordinates
			}}
			>
			<div className={`transition-all duration-250 ease-out absolute top-0 left-0 w-full h-full  ${
					isVisible ? "opacity-100 scale-100 pointer-events-auto" : "opacity-0 scale-95 pointer-events-none"}`}
			>
				<DraggableObject id={id} position={position} label={label} onClose={() => setIsVisible(false)}>
					<div className="w-full">
						{children}
					</div>
				</DraggableObject>
			</div>
			</DndContext>
		</div>
	);
}

function DraggableObject({ id, position, label, children, onClose }) {
	const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({ id });				// Returns all the attributes necessary to make an object Draggable

	const style = {
		position: "absolute",
		top: position.y,																					// Real layout position from which the delta is calculated
		left: position.x,
		transform: `translate3d(${transform ? transform.x : 0}px, ${transform ? transform.y : 0}px, 0)`,	// Position defined relatively to parent, changes while dragging
		zIndex: isDragging ? 1000 : 1,																		// Takes the focus when being dragged
		cursor: 'grab',
	};

	return (
		<div ref={setNodeRef} {...attributes} style={style} className="rounded shadow-md bg-white border border-gray-300 w-4xl absolute">
		{/* |_ The whole div becomes draggable by giving it the 'setNodeRef' and 'attributes' */}

			<div className="flex bg-blue-600 text-white rounded-t">
			{/* |_ Header of the window */}

				<div {...listeners} className="cursor-move flex-1 p-2">
				{/* |_ Only this part is draggable since it has 'listeners'*/}
					{label}
				</div>

				<button onClick={onClose} className="ml-auto font-bold text-white hover:text-red-800 pl-3 pr-3">
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