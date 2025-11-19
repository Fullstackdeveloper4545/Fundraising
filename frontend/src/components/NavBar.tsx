"use client";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import Swal from "sweetalert2";

export default function NavBar() {
  const { user, logout } = useAuth();

  const handleLogoutClick = () => {
    Swal.fire({
      title: 'Logout',
      text: 'Are you sure you want to log out?',
      icon: 'question',
      showCancelButton: true,
      // rely on custom classes for buttons to adapt to theme
      confirmButtonColor: undefined as unknown as string,
      cancelButtonColor: undefined as unknown as string,
      confirmButtonText: 'Yes, logout!',
      cancelButtonText: 'Cancel',
      width: '600px',
      backdrop: `
        rgba(0,0,0,0.4)
        left top
        no-repeat
      `,
      buttonsStyling: false,
      customClass: {
        popup: 'swal2-popup-custom',
        container: 'swal2-backdrop-blur',
        confirmButton: 'btn-logout',
        cancelButton: 'btn-outline'
      }
    }).then((result) => {
      if (result.isConfirmed) {
        logout();
        Swal.fire({
          title: 'Logged out!',
          text: 'You have been successfully logged out.',
          icon: 'success',
          timer: 2000,
          showConfirmButton: false,
          width: '450px'
        });
      }
    });
  };
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-[#00AFF0]/90 backdrop-blur-sm">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-semibold pl-4 sm:pl-6">
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-[#00AFF0] text-sm font-bold text-white">HS</span>
          <span className="text-lg text-white">HighSchool Fund</span>
        </Link>
        <nav className="flex items-center gap-2 sm:gap-4 text-sm pr-4 sm:pr-6">
          <Link href="/campaigns" className="hidden sm:inline hover:underline text-white">Campaigns</Link>
          {user && ["student", "admin"].includes(user.role) && (
            <Link href="/create-campaign" className="hidden sm:inline hover:underline text-white">Create</Link>
          )}
          <Link href="/spotlight" className="hidden sm:inline hover:underline text-white">Spotlight</Link>
          <Link href="/partnership" className="hidden sm:inline hover:underline text-white">Partnership</Link>
          {user ? (
            <div className="flex items-center gap-2 sm:gap-3">
              <span className="hidden sm:inline text-white text-sm">{user.email}</span>
              <button 
                onClick={handleLogoutClick} 
                className="rounded-lg bg-white/20 px-3 py-2 text-white text-sm font-medium hover:bg-white/30 transition-colors"
              >
                Logout
              </button>
            </div>
          ) : (
            <>
              <Link href="/signin" className="hidden sm:inline hover:underline text-sm text-white">Sign in</Link>
              <Link href="/signup" className="btn-primary text-sm">Sign up</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}


