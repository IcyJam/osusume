import DraggableWindow 				from "./components/DraggableWindow";
import QueryForm 					from "./components/QueryForm";
import { DndContext } 				from "@dnd-kit/core";
import { restrictToWindowEdges } 	from "@dnd-kit/modifiers";

export default function App() {
  return (
	// Context that wraps around the draggable elements, makes it so that they can't go over the screen's borders
	<DndContext modifiers={[restrictToWindowEdges]}>
		<div className="p-4">
			<DraggableWindow id="welcomeWindow" label="お勧め" buttonIcon="/folder.png" headerColor="blue">

				<header>
					<h1 className='flex justify-center items-center text-blue-400 pb-2 font-m-plus font-light'>Welcome to Osusume!</h1>
					<h2 className='flex justify-center items-center text-blue-300 font-m-plus font-light text-3xl'>お勧めへようこそ!</h2>
				</header>
				<QueryForm />
				
			</DraggableWindow>

			<DraggableWindow id="welcomeWindow2" label="ほう…向かってくるのか。" buttonIcon="/folder.png" headerColor="yellow">

				<div className="flex justify-center text-black w-lg">
					<img src="/jjba_placeholder.png" />
				</div>
				
			</DraggableWindow>

			<DraggableWindow id="welcomeWindow3" label="このディオだッ!" buttonIcon="/folder.png" headerColor="cyan">

				<div className="flex justify-center text-black w-50">
					<img src="/jjba_placeholder2.jpeg" />
				</div>
				
			</DraggableWindow>
		</div>
		
	</DndContext>
  );
}