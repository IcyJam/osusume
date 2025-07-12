import { useState } from "react";
import { DndContext, useDraggable } from "@dnd-kit/core";
import { restrictToWindowEdges } from "@dnd-kit/modifiers";

export default function DraggableWindow({ id, children, label }) {
	const [position, setPosition] = useState({ x: 100, y: 100 });					// Committed position, i.e. position before/after being dragged

	// Drag context wraps the draggable element
	return (
		<DndContext
			modifiers={[restrictToWindowEdges]}										// Makes it so that the draggable window can't go over the screen's borders
			onDragEnd={({ delta }) => {												// Called when the user stops dragging
			setPosition((p) => ({ x: p.x + delta.x, y: p.y + delta.y }));			// Adds the last drag delta to the committed coordinates
		}}
		>
			<DraggableObject id={id} position={position} label={label}>
				{children}
			</DraggableObject>
		</DndContext>
	);
}

function DraggableObject({ id, position, label, children }) {
	const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({ id });			// Returns all the attributes necessary to make an object Draggable

	// Compute style combining committed position + current drag transform (during drag)
	const style = {
		position: "absolute",
		top: position.y,																				// Real layout position from which the delta is calculated
		left: position.x,
		transform: `translate3d(${transform ? transform.x : 0}px, ${transform ? transform.y : 0}px, 0)`,	// Position defined relatively to parent, changes while dragging
		zIndex: isDragging ? 1000 : 1,																// Takes the focus when being dragged
		cursor: 'grab',
	};

	return (
		<div ref={setNodeRef} {...attributes} style={style} className="rounded shadow-md bg-white border border-gray-300 w-4xl absolute">

			{/* Only this area is draggable */}
			<div {...listeners} className="cursor-move bg-blue-600 text-white px-4 py-2 rounded-t">
				{label}
			</div>

			{/* Other content inside — like form, input, etc. */}
			<div className="p-4">
				{children}
			</div>
		</div>
	);
}