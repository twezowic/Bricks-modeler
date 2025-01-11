import Main from "./Builder/Main";
import Loader from "./YourSets/Loader";
import Profile from "./Account/profile";
import SetsList from "./Browse/SetsList";

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