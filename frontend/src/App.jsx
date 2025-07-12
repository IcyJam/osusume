// import './App.css'
import QueryForm from './components/QueryForm';

import { useState } 		from 'react';
import { DndContext } 		from '@dnd-kit/core';
import { DraggableWindow } 	from './components/DraggableWindow';

import {restrictToWindowEdges, restrictToParentElement, restrictToHorizontalAxis} from '@dnd-kit/modifiers';

export default function App() {
	
	const [position, setPosition] = useState({ x: 0, y: 0 });		// Defines the initial position of the window

	const handleDragEnd = (event) => { 								// Called  the user stops dragging the window
		const { delta } = event;									// Gets the delta parameter of the onDragEndEvent (position variation of the Draggable object)                       
			// |_ Equivalent to 'const delta = event.delta'
		setPosition((prev) => (										// Takes the previous value of the "position" state
			{ x: prev.x + delta.x , y: prev.y + delta.y,}			// Returns the updated position using the delta
		));															
	};																// Only handles the end position, the position during drag is handled in DraggableWindow

	return (
		<div className="w-screen h-screen relative overflow-hidden">

			<div className="w-full h-full">
				<DndContext onDragEnd={handleDragEnd} modifiers={[restrictToWindowEdges]} >
					<DraggableWindow id="draggable" position={position} label="お勧め">

						<header>
							<h1 className='flex justify-center items-center text-blue-400 pb-2 font-m-plus font-light'>Welcome to Osusume!</h1>
							<h2 className='flex justify-center items-center text-blue-300 font-m-plus font-light text-3xl'>お勧めへようこそ!</h2>
						</header>
						<QueryForm />

					</DraggableWindow>
				</DndContext>
			</div>

		</div>
	);
}
