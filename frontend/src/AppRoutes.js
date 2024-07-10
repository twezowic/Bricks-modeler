import Main from "./Main";
import Loader from "./Loader";

const AppRoutes = [
    {
    index: true,
    element: <Main />
    },
    {
    path: '/loader',
    element: < Loader />
    },
];

export default AppRoutes;