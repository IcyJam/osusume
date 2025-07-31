import DraggableWindow 				from "./components/DraggableWindow";
import QueryForm 					from "./components/QueryForm";
import { DndContext } 				from "@dnd-kit/core";
import { restrictToWindowEdges } 	from "@dnd-kit/modifiers";

export default function App() {
  return (
	// Context that wraps around the draggable elements, makes it so that they can't go over the screen's borders
	<DndContext modifiers={[restrictToWindowEdges]}>
		<div className="p-4">
			<div>
			<DraggableWindow id="welcomeWindow" label="お勧め" buttonIcon="/folder.png">

				<header>
					<h1 className='flex justify-center items-center text-blue-400 pb-2 font-m-plus font-light'>Welcome to Osusume!</h1>
					<h2 className='flex justify-center items-center text-blue-300 font-m-plus font-light text-3xl'>お勧めへようこそ!</h2>
				</header>
				<QueryForm />
				
			</DraggableWindow>
			</div>
			<DraggableWindow id="welcomeWindow2" label="お勧め" buttonIcon="/folder.png">

				<header>
					<h1 className='flex justify-center items-center text-blue-400 pb-2 font-m-plus font-light'>Welcome to Osusume!</h1>
					<h2 className='flex justify-center items-center text-blue-300 font-m-plus font-light text-3xl'>お勧めへようこそ!</h2>
				</header>
				<QueryForm />
				
			</DraggableWindow>
		</div>
	</DndContext>
  );
}