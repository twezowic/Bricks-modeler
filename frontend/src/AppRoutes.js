import Main from "./Builder/Main";
import Loader from "./Loader";
import Profile from "./Account/profile";

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
];

export default AppRoutes;