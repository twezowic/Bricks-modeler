import * as React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';


export default function SaveDialog({ saveTrack, updateTrack, trackId }) {
    const [open, setOpen] = React.useState(false);
    const [name, setName] = React.useState('');
  
    const handleClickOpen = () => {
      setOpen(true);
    };
  
    const handleClose = () => {
      setOpen(false);
      setName('');
    };
  
    const handleSave = () => {
      saveTrack(name);
      handleClose();
    };

    const handleOverwrite = () => {
        updateTrack(trackId);
        handleClose();
    }
  
    return (
      <React.Fragment>
        <button className='px-2 py-2 rounded-[8px] bg-white' onClick={handleClickOpen}>
          Save track
        </button>
        <Dialog
          open={open}
          onClose={handleClose}
        >
          <DialogTitle>{trackId ? 'Overwrite or Save New?' : 'Save Model Track'}</DialogTitle>
          <DialogContent>
            <DialogContentText>
              {trackId
                ? 'A model track with this ID already exists. You can overwrite it or create a new one.'
                : 'Enter a name for your model track.'}
            </DialogContentText>
                <TextField
                autoFocus
                margin="dense"
                id="name"
                label="Track Name"
                type="text"
                fullWidth
                variant="standard"
                value={name}
                onChange={(e) => setName(e.target.value)}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose} variant={'info'}>Cancel</Button>
            <Button type="button" onClick={handleSave}>{trackId ? "Create new one" : "Save"}</Button>
            {trackId && <Button type="button" onClick={handleOverwrite}>Overwrite</Button>}
          </DialogActions>
        </Dialog>
      </React.Fragment>
    );
  }