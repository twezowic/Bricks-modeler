import Main from "./Builder/Main";
import Loader from "./Loader";
import Profile from "./Account/profile";
import SetsList from "./Explorer/SetsList";

const AppRoutes = [
    {
    index: true,
    element: <Main />
    },
    {
    path: '/loader',
    element: < Loader />
    },
    {
    path: '/profile',
    element: <Profile />
    },
    {
    path: '/sets',
    element: <SetsList />
    },
];

export default AppRoutes;