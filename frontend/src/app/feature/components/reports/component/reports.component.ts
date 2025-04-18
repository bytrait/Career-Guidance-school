import { Component } from '@angular/core';
import { DatePipe } from '@angular/common';
import { Route, Router } from '@angular/router';
import { Unsubscribable } from 'rxjs';
import { PERSONALITY_TEST_RESULT } from 'src/app/core/constants';
import { AuthService } from 'src/app/shared/services/auth.service';
import { CareerOptionsService } from 'src/app/shared/services/career-options.service';
import { CareerTestService } from 'src/app/shared/services/career-test.service';
import { PersonalityTestService } from 'src/app/shared/services/personality-test.service';
import { ReportsService } from 'src/app/shared/services/reports.service';
import { StudentReportService } from 'src/app/shared/services/student-report.service';
import { ViewChild } from '@angular/core';
import { jsPDF } from 'jspdf';
import { BarChartComponent } from './bar-chart/bar-chart.component';
import { Top3PersonalityStrengthsComponent } from './top3-personality-strengths/top3-personality-strengths.component';
import { CareerInterestsComponent } from './career-interests/career-interests.component';
import { CareerOptionsComponent } from './career-options/career-options.component';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.scss']
})
export class ReportsComponent {

  @ViewChild(BarChartComponent) barChartComponent: BarChartComponent;
  @ViewChild(Top3PersonalityStrengthsComponent) top3PersonalityComponent: Top3PersonalityStrengthsComponent;
  @ViewChild(CareerInterestsComponent) careerInterestsComponent : CareerInterestsComponent;

  @ViewChild(CareerOptionsComponent) careerOptionsComponent: CareerOptionsComponent;
  isReportAvaiable: boolean = false;

  isLoader: boolean = true;
  suggestedCareers: any = []
  careerStream: string = ''
  personalityTestResults: any;
  unsubscribeTestReports: Unsubscribable;
  unsubscribeTitle: Unsubscribable;
  careerTestResults: any
  careerTitle: string = ''
  preferredCareer: string;
  showChat: boolean = false;
  question: string;
  chatData: any;
  showReport: boolean = false;
  chatLimitExceeded: boolean = false;
  constructor(
    private _router: Router,
    private _personalityTestService: PersonalityTestService,
    private _careerTestService: CareerTestService,
    private _authService: AuthService,
    private _reportService: ReportsService,
    private _studReportService: StudentReportService,
    private datePipe: DatePipe,
    private _careerOptionsService: CareerOptionsService) {
  }
  ngOnInit() {


    let data = localStorage.getItem(PERSONALITY_TEST_RESULT);

    if (data) {
      this.isReportAvaiable = JSON.parse(data) ? true : false
    } else {
      this.isReportAvaiable = this._authService.isReportGenerated()
    }
    if (this.isReportAvaiable) {
      this.showReport = true;
    }
    if (this._authService.isReportGenerated()) {
      this.isLoader = true;
      this.unsubscribeTestReports = this._careerTestService.getTestReports().subscribe({
        next: (result) => {
          if (result.success) {
            this._reportService.setReports(result);
            const { careerInterestData, careerOptions, preferredCareer } = result.reportData;
            let personalityData = {
              ...result?.reportData?.personalityData
            }
            this.preferredCareer = preferredCareer;
            //  this._personalityTestService.setPersonalityTestResult({ personalityData });
            // this._careerTestService.setCareerTestResult(careerInterestData);
            // this.suggestedCareers = careerOptions?.suggestedCareers
            //  this.personalityTestResults = personalityData
            this.careerTestResults = careerInterestData
            this.isReportAvaiable = true;
            this.showReport = true;
            this.isLoader = false;
          } else {
            this.isLoader = false;
          }
        }, error: (error) => {
          if (error.status === 403 && error.error.message === 'Payment not done') {
            this._router.navigate(['dashboard/payment']);
          }
          this.isLoader = false;
        }
      })
    } else {
      this.isLoader = false;
    }
  }

  ngAfterViewInit() {
    setTimeout(() => {
      console.log(this.careerOptionsComponent.getCareerList())
    }, 3000);

    this.unsubscribeTitle = this._careerOptionsService.getCareerTitle().subscribe((res) => {
      if (Object.keys(res).length > 0) {
        setTimeout(() => {
          let el = document.getElementById('careerModelPath');
          el?.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
            inline: "nearest"
          })
        }, 0);
      } else {
        setTimeout(() => {
          let el = document.querySelector('.page-wrapper');
          el?.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
            inline: "nearest"
          })
        }, 0);
      }
    })
  }

  onClickGetTitle(title: string) {
    this.careerTitle = title;
  }

  gotAssessment() {
    this._router.navigate(['dashboard/welcome'])
  }

  openReport() {
    this.showReport = true;
    this.showChat = false;
  }

  openChat() {
    this.showChat = true;
    this.showReport = false;
    this.question = '';
    this.isLoader = true;
    // call API to get chat data
    this._studReportService.getUserChat().subscribe({
      next: (result) => {
        this.isLoader = false;
        if (result.success) {
          this.chatData = result.chatData;
          if (this.chatData) {
            this.chatData.chatHistory.forEach((chat: any) => {
              chat.chatTime = this.datePipe.transform(new Date(chat.chatTime), 'dd/MM/yyyy HH:mm:ss') || 'Invalid date';
            });
            if (result.tokenUsed >= 500) {
              this.chatLimitExceeded = true;
            }
          }
        } else {
          this.isLoader = false;
        }
      }, error: (error) => {
        this.isLoader = false;
      }
    }
    )
  }

  sendQuestion() {
    this.isLoader = true;
    // call API to get chat data
    this._studReportService.getChatAnswer(this.question).subscribe({
      next: (result) => {
        this.question = '';
        this.isLoader = false;
        if (result.success) {
          this.chatData = result.chatData;
          if (this.chatData) {
            this.chatData.chatHistory.forEach((chat: any) => {
              chat.chatTime = this.datePipe.transform(new Date(chat.chatTime), 'dd/MM/yyyy HH:mm:ss') || 'Invalid date';
            });
            if (result.tokenUsed >= 500) {
              this.chatLimitExceeded = true;
            }
          }
        } else {
          this.isLoader = false;
        }
      }, error: (error) => {
        this.question = '';
        this.isLoader = false;
      }
    }
    )
  }

  formatDate(dateStr: string) {
    if (dateStr) {
      const date = new Date(dateStr);
      return this.datePipe.transform(date, 'dd/MM/yyyy HH:mm:ss') || '';
    }
    return '';
  }

  ngOnDestory() {
    if (this.unsubscribeTestReports) this.unsubscribeTestReports;
    if (this.unsubscribeTitle) this.unsubscribeTitle;

  }

  getTopPersonalityTraits(data: any): { type: string, score: number }[] {
    if (!data) return [];

    const traits = [
      { type: data?.aPersonality?.type, score: data?.aPersonality?.score },
      { type: data?.cPersonality?.type, score: data?.cPersonality?.score },
      { type: data?.ePersonality?.type, score: data?.ePersonality?.score },
      { type: data?.nPersonality?.type, score: data?.nPersonality?.score },
      { type: data?.oPersonality?.type, score: data?.oPersonality?.score },
    ];

    return traits
      .filter(trait => trait.type && trait.score !== undefined)
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);
  }

  getTop3PersonalityData(): { type: string, score: number, description: string, strength: string }[] {
    return this.top3PersonalityComponent?.getTopPersonalityTraits() || [];
  }

  loadImageAsBase64(path: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'Anonymous';
      img.src = path;

      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        ctx?.drawImage(img, 0, 0);
        resolve(canvas.toDataURL('image/png'));
      };

      img.onerror = err => reject(err);
    });
  }


  async downloadReport(): Promise<void> {
    const doc = new jsPDF();
    const pageHeight = doc.internal.pageSize.height;
    const pageWidth = doc.internal.pageSize.width;

    let y = 30; // Content Y position after header
    let currentPage = 1;

    const logoBase64 = await this.loadImageAsBase64('/assets/images/bytrait_logo.png');
    const reportDate = new Date().toLocaleDateString();

    const addHeader = () => {
      if (logoBase64) {
        doc.addImage(logoBase64, 'PNG', 10, 5, 30, 20);
      }
      doc.setFontSize(14);
      doc.text('Career Report', pageWidth / 2, 15, { align: 'center' });
      doc.setLineWidth(0.5);
      doc.line(10, 22, pageWidth - 10, 22);
    };

    const addFooter = () => {
      doc.setLineWidth(0.5);
      doc.line(10, pageHeight - 15, pageWidth - 10, pageHeight - 15);
      doc.setFontSize(10);
      doc.text(`Date: ${reportDate}`, 10, pageHeight - 10);
      doc.text(`Page ${currentPage}`, pageWidth - 10, pageHeight - 10, { align: 'right' });
    };

    const addNewPage = () => {
      doc.addPage();
      currentPage++; // Increase after adding new page
      y = 30; // Reset Y position
      addHeader();
      addFooter();
    };

    const addText = (text: string, fontSize: number, indent = 10, lineHeight = 10, color: [number, number, number] = [0, 0, 0]) => {
      doc.setFontSize(fontSize);
      doc.setTextColor(...color);
      if (y + lineHeight > pageHeight - 20) {
      addNewPage();
      }
      doc.text(text, indent, y);
      y += lineHeight;
    };

    // First page setup
    addHeader();
    addFooter();


    const top3 = this.getTop3PersonalityData();
    addText('Your Top Personality Strengths', 12,10,5);
    addText("The following section shows your top personality strengths based on your resposes to the 50 question personality test",9)
    top3.forEach((item, i) => {
      addText(`${i + 1}. ${item.strength}`, 12, 10, 5);

      doc.setFontSize(10);
      const lines = doc.splitTextToSize(`${item.description}`, 180);
      lines.forEach((line: string, index: number) => {
        if (y + 6 > pageHeight - 20) {
          addNewPage();
        }
        doc.text(line, 20, y);
        y += 6;
      });
      y += 8; 
      doc.setFontSize(12);
    });

    // Chart image
    const chartImage = this.top3PersonalityComponent.barChartComponent?.getChartImage();
    if (chartImage) {
      const chartHeight = 90;
      if (y + chartHeight > pageHeight - 20) {
        addNewPage();
      }
      const chartWidth = 180;
      const chartX = (pageWidth - chartWidth) / 2; // Center the image horizontally
      doc.addImage(chartImage, 'PNG', chartX, y, chartWidth, chartHeight);
      y += chartHeight + 10;
    }



    // Career summary
    addText('Your career interests', 14,10,5);
    addText("The following section shows the type of work you would enjoy the most based on your responses to the 30 question career interest test.", 9);

    
    const careerInterestAcc = this.careerInterestsComponent?.getCareerInterestAcc();
    if (careerInterestAcc) {
      careerInterestAcc.forEach((item: any) => {
        addText(`${item.riasecType}`, 12, 10, 5);
        doc.setFontSize(10);
        const lines = doc.splitTextToSize(`${item.description}`, 180);
        lines.forEach((line: string) => {
          if (y + 6 > pageHeight - 20) {
            addNewPage();
          }
          doc.text(line, 20, y);
          y += 6;
        });
        y += 8;
      });
    }

    const radarImage = this.careerInterestsComponent?.getRadarChartImage();
    const radarImageHeight = 90; // Height of the radar image
    if (radarImage) {
      if (y + radarImageHeight > pageHeight - 20) {
        addNewPage();
      }
      doc.addImage(radarImage, 'PNG', 10, y, 90, radarImageHeight);
      y += radarImageHeight + 10; // Add some spacing after the image
    }

    addText(`Career Options`, 14, 10, 5);
    addText("The following section shows the career options based on your personality and career interest test results.", 9);
    const careerOptions = this.careerOptionsComponent?.getCareerList();
    if (careerOptions) {
      careerOptions.forEach((item: any) => {
        addText(`${item.careerTitle}`, 12,10,5);
        doc.setFontSize(10);
        const lines = doc.splitTextToSize(`${item.careerDescription}`, 180);
        lines.forEach((line: string) => {
          if (y + 6 > pageHeight - 20) {
            addNewPage();
          }
          doc.text(line, 20, y);
          y += 6;
        });
        y += 8;
      });
    }    

    addText(`To explore the complete career path, please visit our website:`, 12, 10, 5);
    addText(`https://school.bytrait.com/`, 10, 20, 5, [0, 0, 255]);
    // Save PDF
    doc.save(`career-report-from-bytrait${new Date().toISOString().slice(0, 10)}.pdf`);
  }





}
