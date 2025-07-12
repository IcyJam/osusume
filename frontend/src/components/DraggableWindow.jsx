import { useDraggable } from '@dnd-kit/core';

export function DraggableWindow({ id, position, children, label}) {

    const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({id,});       // Returns all the attributes necessary to make an object Draggable
    
    const x = position.x + (transform?.x || 0);         // Only handles the position during dragging, the end position is handled with setPosition
    const y = position.y + (transform?.y || 0);                                    

    const style = {
        transform: `translate3d(${x}px, ${y}px, 0)`,
        position: 'absolute',                           // Position defined relatively to parent
        zIndex: isDragging ? 1000 : 1,                  // Takes the focus when being dragged
    };

	// The object that has 'setNodeRef' and 'attributes' is Draggable, but only the part of the object that has 'listeners' can be used as a handle to move it
    return (
        <div ref={setNodeRef} {...attributes} style={style} className="rounded shadow-md bg-white border border-gray-300 absolute w-4xl">
			<div {...listeners} className="cursor-move bg-blue-600 text-white px-4 py-2 rounded-t">
				{label}
			</div>
			<div className="p-4">							
				{children}
			</div>
        </div>
  );
}