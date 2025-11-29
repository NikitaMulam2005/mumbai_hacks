import { useState } from "react";
import { NavLink } from "react-router-dom";

const Navbar = () => {
  const [open, setOpen] = useState(false);

  const linkStyle = ({ isActive }) =>
    `px-3 py-1 rounded-md border transition-all
    ${isActive ? "border-cyan-600 bg-cyan-400 text-white" : "border-transparent text-white"}
    hover:border-white/50`;


  return (
    <>
      {/* <div className="bg-[url('/mumbai-skyline1.jpg')] min-h-screen bg-cover bg-no-repeat bg-fixed"></div> */}

      <nav className="backdrop-blur-md z-1 bg-white/30 border border-white/5 shadow-lg fixed top-0 left-0 w-full">
        <div className="max-w-full ml-10 flex items-center justify-between mr-20">

          <NavLink to="/" className="text-2xl font-bold tracking-wide flex items-center">
            <img src="/favicon2.svg" alt="Home" className="h-18 ml-0 mr-6 mt-2" />
            <div className="text-4xl text-cyan-300 pb-3">TruthPulse</div>
          </NavLink>

          {/* Desktop Links */}
          <div className="hidden md:flex gap-8 text-lg my-auto ">
            <NavLink to="/" className={linkStyle}>Home</NavLink>
            <NavLink to="/analytics" className={linkStyle}>Analytics</NavLink>
            <NavLink to="/about" className={linkStyle}>About</NavLink>
            <NavLink to="/contact" className={linkStyle}>Contact</NavLink>
          </div>

          <button 
            className="md:hidden text-3xl"
            onClick={() => setOpen(!open)}
          >
            {open ? "✕" : "☰"}
          </button>
        </div>

        {/* Mobile Menu */}
        {open && (
          <div className="md:hidden mt-4 flex flex-col gap-4 text-lg bg-gray-800 p-4 rounded-lg">
            <NavLink to="/" className={linkStyle} onClick={() => setOpen(false)}>Home</NavLink>
            <NavLink to="/analytics" className={linkStyle} onClick={() => setOpen(false)}>Analytics</NavLink>
            <NavLink to="/about" className={linkStyle} onClick={() => setOpen(false)}>About</NavLink>
            <NavLink to="/contact" className={linkStyle} onClick={() => setOpen(false)}>Contact</NavLink>
          </div>
        )}
      </nav>


    </>
  );
};

export default Navbar;





            {/* <h2>Hello World</h2>
            <div>{import.meta.env.VITE_APP_API_URL}</div>        
            <h1 className="text-center text-lg text-blue-500 underline" onClick={(e) => {console.log("H1 clicked"); console.log(e.target.tagName);}}>Hello World</h1>
            <p className="font-sans">Lorem ipsum dolor sit, amet consectetur adipisicing elit. Suscipit, alias harum repellat fugiat maxime possimus quaerat eos eligendi aspernatur, animi aliquam ea debitis beatae dolore quia neque odit! Nulla ipsa quia officia atque sunt voluptates ipsam, aliquid quos. Corporis optio possimus corrupti ipsa ut molestias expedita! Molestiae reiciendis sapiente magnam tenetur maiores incidunt omnis quas nulla aperiam, reprehenderit voluptas debitis modi quam soluta aspernatur mollitia id suscipit tempore consequuntur? Ducimus magni voluptatem quam praesentium, veritatis minima nobis modi qui aliquid facere ipsum, molestias excepturi atque sint dicta doloremque sapiente beatae quaerat unde recusandae ab facilis a quia! Quibusdam sint cupiditate nihil enim sequi molestiae non incidunt ullam, ipsa, fugiat libero porro assumenda a eum voluptatibus, laborum optio velit tempora nobis. In mollitia expedita aliquam aut neque nam fuga placeat enim doloremque obcaecati reiciendis debitis quis earum, temporibus fugit. Quisquam, non. Molestiae iste, porro ducimus quas deserunt ipsum sequi culpa! Minus, magni quas aut, non laborum tempora similique perspiciatis unde aspernatur debitis nam perferendis reprehenderit consequuntur, ducimus doloribus eveniet blanditiis facilis delectus eius et illo saepe dolor. Optio repellat obcaecati eum labore ex animi ut nesciunt ipsum vel odio fugit, laudantium totam magni? Recusandae ipsa esse, soluta expedita accusantium odit fugiat!</p>
            <br /><br />
            <p className="font-serif text-red-900">Lorem ipsum dolor sit, amet consectetur adipisicing elit. Suscipit, alias harum repellat fugiat maxime possimus quaerat eos eligendi aspernatur, animi aliquam ea debitis beatae dolore quia neque odit! Nulla ipsa quia officia atque sunt voluptates ipsam, aliquid quos. Corporis optio possimus corrupti ipsa ut molestias expedita! Molestiae reiciendis sapiente magnam tenetur maiores incidunt omnis quas nulla aperiam, reprehenderit voluptas debitis modi quam soluta aspernatur mollitia id suscipit tempore consequuntur? Ducimus magni voluptatem quam praesentium, veritatis minima nobis modi qui aliquid facere ipsum, molestias excepturi atque sint dicta doloremque sapiente beatae quaerat unde recusandae ab facilis a quia! Quibusdam sint cupiditate nihil enim sequi molestiae non incidunt ullam, ipsa, fugiat libero porro assumenda a eum voluptatibus, laborum optio velit tempora nobis. In mollitia expedita aliquam aut neque nam fuga placeat enim doloremque obcaecati reiciendis debitis quis earum, temporibus fugit. Quisquam, non. Molestiae iste, porro ducimus quas deserunt ipsum sequi culpa! Minus, magni quas aut, non laborum tempora similique perspiciatis unde aspernatur debitis nam perferendis reprehenderit consequuntur, ducimus doloribus eveniet blanditiis facilis delectus eius et illo saepe dolor. Optio repellat obcaecati eum labore ex animi ut nesciunt ipsum vel odio fugit, laudantium totam magni? Recusandae ipsa esse, soluta expedita accusantium odit fugiat!</p>
            <br /><br />
            <p className="font-mono bg-amber-200 h-[100px]">Lorem ipsum dolor sit, amet consectetur adipisicing elit. Suscipit, alias harum repellat fugiat maxime possimus quaerat eos eligendi aspernatur, animi aliquam ea debitis beatae dolore quia neque odit! Nulla ipsa quia officia atque sunt voluptates ipsam, aliquid quos. Corporis optio possimus corrupti ipsa ut molestias expedita! Molestiae reiciendis sapiente magnam tenetur maiores incidunt omnis quas nulla aperiam, reprehenderit voluptas debitis modi quam soluta aspernatur mollitia id suscipit tempore consequuntur? Ducimus magni voluptatem quam praesentium, veritatis minima nobis modi qui aliquid facere ipsum, molestias excepturi atque sint dicta doloremque sapiente beatae quaerat unde recusandae ab facilis a quia! Quibusdam sint cupiditate nihil enim sequi molestiae non incidunt ullam, ipsa, fugiat libero porro assumenda a eum voluptatibus, laborum optio velit tempora nobis. In mollitia expedita aliquam aut neque nam fuga placeat enim doloremque obcaecati reiciendis debitis quis earum, temporibus fugit. Quisquam, non. Molestiae iste, porro ducimus quas deserunt ipsum sequi culpa! Minus, magni quas aut, non laborum tempora similique perspiciatis unde aspernatur debitis nam perferendis reprehenderit consequuntur, ducimus doloribus eveniet blanditiis facilis delectus eius et illo saepe dolor. Optio repellat obcaecati eum labore ex animi ut nesciunt ipsum vel odio fugit, laudantium totam magni? Recusandae ipsa esse, soluta expedita accusantium odit fugiat!</p>
            <button className="btn">Click me</button>
            <button type="submit" className="border-2 " onClick={(e) => {console.log("Button clicked"); console.log(e.target.tagName);}}>Hello</button>
            
            
            <div className="container mt-10 text-center m-auto w-160 h-75 rounded border-2 border-black">
                <div className="quote rounded-t w-full text-white bg-gradient-to-r from-sky-500 to-indigo-500 h-20 text-center font-bold flex items-center justify-center">News you can trust</div>
                <div className="content h-55 ">
                    <h2 className="font-bold mt-4">Stay up to date with the Latest!</h2>
                    <p>Subscribe to our newsletter for the latest news straight into your inbox</p>
                    <input type="email" placeholder="you@example.com" className="bg-gray-300 rounded  w-70 flex justify-center text-center h-10 my-3 mx-auto placeholder:text-sm "/>
                    <button className="bg-blue-500 rounded-full text-white p-2 w-70 mb-3">Subscribe Now</button>
                    <p>We value your privacy</p>
                </div>
            </div>

            text-[min(10vw, 70px)] for screen fluid text

            Glassmorphism
            <div className="bg-[url('/mumbai-skyline1.jpg')] min-h-screen bg-cover bg-no-repeat bg-fixed border  bg-cover mx-0 py-0">
                <div className="card w-80 rounded-2xl border border-white/20 shadow-lg backdrop-filter backdrop-blur-md p-6 h-100 bg-white/10 m-auto my-20">YT</div>
                <div className="check p-6 backdrop-blur-md bg-white/20 border border-white/30 shadow-lg rounded-xl h-100 w-80 m-auto my-20">Chatgpt</div>
            </div> */}