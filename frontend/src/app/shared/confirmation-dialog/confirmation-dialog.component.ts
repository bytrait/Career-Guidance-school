import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA  } from '@angular/material/dialog';

@Component({
  selector: 'app-confirmation-dialog',
  templateUrl: './confirmation-dialog.component.html',
  styleUrls: ['./confirmation-dialog.component.scss']
})
export class ConfirmationDialogComponent {

  constructor(
    public dialogRef: MatDialogRef<ConfirmationDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { message: string, title: string } // Accept data here
  ) {}

  confirm() {
    this.dialogRef.close(true); // Pass true on confirmation
  }

  close() {
    this.dialogRef.close(false); // Pass false on cancellation
  }

}
