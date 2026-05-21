import { forwardRef } from 'react';
import './InputBox.css'

const InputBox = forwardRef((props, ref) => {
    const changehandler = (event) => {
        props.onChange(event)
    }

    return <input   ref={ref}
                    className={`input ${!(props.isValid) ? 'inValid' : ''}`} 
                    onChange={changehandler}  
                    type={props.type} 
                    placeholder={props.defualt}
                    style={props.style}></input>
});

export default InputBox