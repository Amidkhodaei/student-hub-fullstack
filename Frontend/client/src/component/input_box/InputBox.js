import './InputBox.css'

const InputBox = (props) => {
    const changehandler = (event) => {
        props.onChange(event)
    }

    return <input   className={`input ${!(props.isValid) ? 'inValid' : ''}`} 
                    onChange={changehandler}  
                    type={props.type} 
                    placeholder={props.defualt}
                    style={props.style}></input>
}

export default InputBox