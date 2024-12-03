import * as Yup from 'yup';


const schema = Yup.object().shape({
    username: Yup.string().required("Please provide your username"),
    password: Yup.string().required("Please provide your password").min(6, "Password is too short - should be 6 chars minimum")

});
export default schema;