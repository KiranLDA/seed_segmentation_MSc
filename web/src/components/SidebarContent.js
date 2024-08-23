import React from "react";
import Header from "./sidebar-components/Header";
import SidebarForm from "./sidebar-components/SidebarForm";

function SidebarContent() {
    return (
        <div className="flex flex-col gap-4 w-full h-full justify-start px-6 py-6 bg-gray-800 shadow-right">
            <Header />
            <SidebarForm />
        </div>
    );
}

export default SidebarContent;