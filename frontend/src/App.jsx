import DraggableWindow 		from "./components/DraggableWindow";
import QueryForm 			from "./components/QueryForm";

export default function App() {
  return (
	<div>
		<DraggableWindow id="welcomeWindow" label="お勧め">

			<header>
				<h1 className='flex justify-center items-center text-blue-400 pb-2 font-m-plus font-light'>Welcome to Osusume!</h1>
				<h2 className='flex justify-center items-center text-blue-300 font-m-plus font-light text-3xl'>お勧めへようこそ!</h2>
			</header>
			<QueryForm />
			
		</DraggableWindow>
	</div>
  );
}