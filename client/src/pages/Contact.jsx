import { Github, Mail, Linkedin, Twitter, Code2, Terminal, GithubIcon } from 'lucide-react';
import { Link } from 'react-router-dom';

const TeamMemberCard = ({ member }) => {
  return (
    <div className="group relative flex flex-col items-center p-6 transition-all duration-300 hover:-translate-y-2">
      {/* Glass Card Background */}
      <div className="absolute inset-0 -z-10 rounded-2xl bg-white/5 border border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.36)] backdrop-blur-md transition-all duration-300 group-hover:bg-white/10 group-hover:border-white/20 group-hover:shadow-[0_8px_32px_0_rgba(31,38,135,0.37)]"></div>
      
      {/* Decorative Gradient Blob behind image */}
      <div className={`absolute top-6 h-24 w-24 rounded-full bg-linear-to-r ${member.gradient} opacity-50 blur-xl transition-all duration-500 group-hover:opacity-80`}></div>

      {/* Content */}
      <div className="text-center">
        <h3 className="text-xl font-bold text-white tracking-wide">{member.name}</h3>
        <p className="mb-4 text-sm font-medium text-blue-200">{member.role}</p>
        
        <p className="mb-6 text-sm text-gray-300 line-clamp-2 px-2">
          {member.bio}
        </p>

            {/* Social Actions */}
            <div className="flex items-center justify-center gap-4">
                <a href={member.github} className="group/icon rounded-full bg-white/5 p-2 text-white transition-all hover:bg-white/20 hover:text-blue-400">
                    <Github size={18} />
                </a>
                <a href={`mailto:${member.email}`} className="group/icon rounded-full bg-white/5 p-2 text-white transition-all hover:bg-white/20 hover:text-blue-400">
                    <Mail size={18} />
                </a>
                <a href={member.linkedin} className="group/icon rounded-full bg-white/5 p-2 text-white transition-all hover:bg-white/20 hover:text-blue-400">
                    <Linkedin size={18} />
                </a>
            </div>
        </div>
    </div>
  );
};


const Contact = () => {
  const teamMembers = [
    {
      name: "Nikita Mulam",
      role: "Agent developer",
      bio: "developing intelligent agents that leverage AI to automate tasks and enhance user experiences.",
      github: "https://github.com/NikitaMulam2005",
      email: "nikitamulam2005@gmail.com",
      linkedin:"https://www.linkedin.com/in/nikita-mulam-a83639287?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app",
      gradient: "from-pink-500 to-rose-500"
    },
    {
      name: "Sharanya Pillai",
      role: "Backend Developer",
      bio: "Designing robust server-side architectures and APIs to power seamless applications.",
      github: "https://github.com/sharanyaa23",
      email: "sharanyavp23@gmail.com",
      linkedin: "https://www.linkedin.com/sharanyapillai",
      gradient: "from-blue-500 to-cyan-500"
    },
    {
      name: "Swarika Maurya",
      role: "Frontend Developer",
      bio: "Crafting intuitive interfaces with a focus on accessibility and motion design.",
      github: "https://github.com/SwarikaaM",
      email: "swarikamaurya@gmail.com",
      linkedin: "https://www.linkedin.com/in/swarikamaurya/",
      gradient: "from-purple-500 to-violet-500"
    }
  ];

  

  return (
    <div className="min-h-screen w-full  text-white selection:bg-blue-500 selection:text-white">
      {/* Background Gradients */}
      <div className="fixed inset-0 -z-10 ">
        <div className="absolute top-0 -left-4 h-72 w-72 rounded-full bg-purple-500 opacity-20 blur-[128px]"></div>
        <div className="absolute bottom-0 right-0 h-96 w-96 rounded-full bg-blue-500 opacity-20 blur-[128px]"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[500px] w-[500px] rounded-full bg-indigo-500 opacity-10 blur-[128px]"></div>
      </div>

      {/* Main Content */}
      <div className="relative  flex flex-col mt-20">
        <main className="mx-auto w-full max-w-7xl grow px-6 py-12">
          
          {/* Header Section */}
          <div className="mb-20 text-center">
            <h2 className="mb-4 text-sm font-bold uppercase tracking-widest text-blue-400">Our Team</h2>
            <h1 className="mb-6 text-4xl font-extrabold tracking-tight text-white md:text-6xl">
              Meet the <span className="text-transparent bg-clip-text bg-linear-to-r from-blue-400 to-purple-500">Visionaries</span>
            </h1>
            <p className="mx-auto max-w-2xl text-lg text-gray-400">
              We are a diverse group of thinkers, builders, and creators dedicated to transforming ideas into reality through code and design.
            </p>
          </div>

          {/* Team Grid */}
          <div className="mb-24 grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
            {teamMembers.map((member, index) => (
              <TeamMemberCard key={index} member={member} />
            ))}
          </div>

          {/* Contact Section Split */}
          <div className="rounded-3xl border border-white/10 bg-black/20 p-8 backdrop-blur-xl md:p-12 ">
            {/* <div className="flex flex-col gap-12 lg:flex-row lg:items-center"> */}
              {/* Left Side: Info */}
              <div className="flex-1 space-y-8">
                <div>
                  <h2 className="text-3xl font-bold text-white mb-4">Project Link</h2>
                  <p className="text-gray-400">
                    Checkout out our project here.
                  </p>
                </div>

                <div>
                  <Link to="" className="flex items-start gap-4">
                    <div className="rounded-lg bg-blue-500/10 p-3 text-blue-400">
                      <GithubIcon size={24} />
                    </div>
                    <div>
                      <h4 className="font-semibold text-white">GitHub Link</h4>
                      <p className="text-sm text-gray-400">Source Code</p>
                    </div>
                  </Link>
                </div>
              </div>
            {/* </div> */}
          </div>

        </main>
      </div>
    </div>
  );
}

export default Contact;