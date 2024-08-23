import React from "react";
import { RequestProvider } from "./RequestContext";
import SidebarContent from "./SidebarContent";

function Sidebar() {
    return (
        <RequestProvider>
            <SidebarContent />
        </RequestProvider>
    );
  }

export default Sidebar;