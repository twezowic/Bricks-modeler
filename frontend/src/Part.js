export default function Part({ imageUrl, name }) {
    return (
        <div>
            <img src={imageUrl} alt={name} />
        </div>
    );
}