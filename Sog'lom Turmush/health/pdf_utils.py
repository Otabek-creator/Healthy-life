from keyword import kwlist

from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Avg, Max, Min, Count
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image
from reportlab.graphics.shapes import Circle, Rect, Polygon
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.graphics.shapes import Drawing, Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
import os
from django.conf import settings
import datetime
from collections import defaultdict

# Modellarni import qilish
from .models import Food, Workout


def download_stats_pdf(request):
    try:
        # Foydalanuvchi ma'lumotlarini olish
        user = request.user
        username = user.username if user.is_authenticated else "Mehmon"
        full_name = getattr(user, 'full_name', username) if user.is_authenticated else "Mehmon"

        # Sana parametrlarini olish
        start_date = request.GET.get('start_date', (timezone.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'))
        end_date = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))

        # Ma'lumotlarni bazadan olish
        foods = Food.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).order_by('date')

        workouts = Workout.objects.filter(
            user=user,
            date__range=[start_date, end_date],
            status='Bajarilgan'  # Faqat bajarilgan mashqlar
        ).order_by('date')

        # Kunlik ma'lumotlarni tayyorlash
        daily_data = defaultdict(lambda: {
            'date': None,
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0,
            'calories_burned': 0,
            'net_calories': 0,
            'meals': defaultdict(list)
        })

        # Ovqatlanish ma'lumotlarini kunlar bo'yicha guruhlash
        for food in foods:
            date_str = food.date.strftime('%Y-%m-%d')
            daily_data[date_str]['date'] = food.date
            daily_data[date_str]['total_calories'] += food.calories
            daily_data[date_str]['total_protein'] += food.protein
            daily_data[date_str]['total_carbs'] += food.carbs
            daily_data[date_str]['total_fat'] += food.fat
            daily_data[date_str]['meals'][food.meal_type].append(food)

        # Mashq ma'lumotlarini kunlar bo'yicha qo'shish
        for workout in workouts:
            date_str = workout.date.strftime('%Y-%m-%d')
            if date_str in daily_data:
                daily_data[date_str]['calories_burned'] += workout.calories_burned
            else:
                daily_data[date_str]['date'] = workout.date
                daily_data[date_str]['calories_burned'] = workout.calories_burned

        # Sof kaloriyalarni hisoblash (qabul qilingan - sarflangan)
        for date_str, data in daily_data.items():
            data['net_calories'] = data['total_calories'] - data['calories_burned']

        # Kunlar bo'yicha tartiblash
        sorted_daily_data = sorted(daily_data.values(), key=lambda x: x['date'])

        # Statistika ma'lumotlarini hisoblash
        if sorted_daily_data:
            avg_calories = sum(day['total_calories'] for day in sorted_daily_data) / len(sorted_daily_data)
            max_calories = max(day['total_calories'] for day in sorted_daily_data)
            min_calories = min(day['total_calories'] for day in sorted_daily_data)
            avg_protein = sum(day['total_protein'] for day in sorted_daily_data) / len(sorted_daily_data)
            avg_carbs = sum(day['total_carbs'] for day in sorted_daily_data) / len(sorted_daily_data)
            avg_fat = sum(day['total_fat'] for day in sorted_daily_data) / len(sorted_daily_data)
            avg_calories_burned = sum(day['calories_burned'] for day in sorted_daily_data) / len(sorted_daily_data)
            avg_net_calories = sum(day['net_calories'] for day in sorted_daily_data) / len(sorted_daily_data)
        else:
            avg_calories = max_calories = min_calories = avg_protein = avg_carbs = avg_fat = avg_calories_burned = avg_net_calories = 0

        # Ovqat turlari bo'yicha statistika
        meal_type_calories = defaultdict(int)
        for food in foods:
            meal_type_calories[food.meal_type] += food.calories

        # PDF yaratish
        buffer = BytesIO()
        # A4 o'lchamini mm da belgilash (210mm x 297mm)
        page_width, page_height = A4

        # PDF yaratish
        pdf = canvas.Canvas(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        # Uslublarni yaratish
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=6 * mm,
            textColor=colors.darkblue
        )

        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=3 * mm,
            textColor=colors.darkblue
        )

        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading3'],
            fontSize=12,
            alignment=TA_LEFT,
            textColor=colors.darkblue
        )

        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            leading=14
        )

        # PDF sarlavha qismi
        def draw_header():
            # Logo (agar mavjud bo'lsa)
            logo_path = os.path.join(settings.MEDIA_ROOT, 'logo.jpg')
            if os.path.exists(logo_path):
                pdf.drawImage(logo_path, 20 * mm, page_height - 35 * mm, width=25 * mm, height=25 * mm, mask='auto')

            # Sarlavha
            pdf.setFont("Helvetica-Bold", 18)
            pdf.setFillColor(colors.darkblue)
            pdf.drawCentredString(page_width / 2, page_height - 20 * mm, "SALOMAT OVQATLANISH STATISTIKASI")

            # Sana oralig'i
            pdf.setFont("Helvetica", 12)
            pdf.drawCentredString(page_width / 2, page_height - 30 * mm, f"Davr: {start_date} dan {end_date} gacha")

            # Foydalanuvchi ma'lumotlari
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(20 * mm, page_height - 45 * mm, f"Foydalanuvchi: {full_name}")

            # Hisobot yaratilgan sana
            pdf.setFont("Helvetica", 10)
            pdf.drawRightString(page_width - 20 * mm, page_height - 45 * mm,
                                f"Hisobot yaratilgan sana: {timezone.now().strftime('%Y-%m-%d %H:%M')}")

            # Ajratuvchi chiziq
            pdf.setStrokeColor(colors.darkblue)
            pdf.setLineWidth(1)
            pdf.line(20 * mm, page_height - 50 * mm, page_width - 20 * mm, page_height - 50 * mm)

        # Kunlik ma'lumotlar jadvalini chizish
        def draw_daily_summary_table():
            # Jadval sarlavhasi
            pdf.setFont("Helvetica-Bold", 14)
            pdf.setFillColor(colors.darkblue)
            pdf.drawString(20 * mm, page_height - 60 * mm, "Kunlik ovqatlanish va faollik xulosasi")

            # Jadval ma'lumotlarini tayyorlash
            table_data = [
                ["Sana", "Qabul qilingan\nkaloriya", "Oqsillar\n(g)", "Yog'lar\n(g)", "Uglevodlar\n(g)",
                 "Sarflangan\nkaloriya", "Sof\nkaloriya"]
            ]

            for day_data in sorted_daily_data:
                date_str = day_data['date'].strftime('%Y-%m-%d')
                table_data.append([
                    date_str,
                    f"{day_data['total_calories']} kcal",
                    f"{day_data['total_protein']:.1f} g",
                    f"{day_data['total_fat']:.1f} g",
                    f"{day_data['total_carbs']:.1f} g",
                    f"{day_data['calories_burned']} kcal",
                    f"{day_data['net_calories']} kcal"
                ])

            # Agar ma'lumot bo'lmasa
            if len(table_data) == 1:
                table_data.append(["Ma'lumot mavjud emas", "", "", "", "", "", ""])

            # Sarlavha qatorini formatlash
            table_data[0] = [Paragraph(f"<b>{cell}</b>", normal_style) for cell in table_data[0]]

            # Jadval o'lchamlari
            table_width = page_width - 40 * mm
            col_widths = [table_width * 0.15, table_width * 0.15, table_width * 0.12,
                          table_width * 0.12, table_width * 0.12, table_width * 0.15, table_width * 0.15]

            table = Table(table_data, colWidths=col_widths)

            # Jadval uslubi
            row_count = len(table_data)
            table.setStyle(TableStyle([
                # Sarlavha qatori
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
            ]))

            # Juft va toq qatorlar uchun ranglar
            for i in range(1, row_count):
                if i % 2 == 0:
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
                    ]))
                else:
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, i), (-1, i), colors.white)
                    ]))

            # Barcha qatorlar uchun umumiy uslub
            table.setStyle(TableStyle([
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('ROWHEIGHT', (0, 0), (-1, -1), 8 * mm),
            ]))

            # Jadvalni PDFga qo'shish
            table.wrapOn(pdf, table_width, 100 * mm)
            table.drawOn(pdf, 20 * mm, page_height - 65 * mm - len(table_data) * 8 * mm)

            return page_height - 65 * mm - len(table_data) * 8 * mm - 10 * mm  # Keyingi element uchun y pozitsiyasi

        # Statistika ma'lumotlarini chizish
        def draw_statistics(y_position):
            # Statistika sarlavhasi
            pdf.setFont("Helvetica-Bold", 14)
            pdf.setFillColor(colors.darkblue)

            pdf.drawString(20 * mm, y_position, "Statistika xulosasi")

            # Statistika ma'lumotlari
            stats_data = [
                ["Ko'rsatkich", "Qiymat"],
                ["O'rtacha kunlik kaloriya", f"{avg_calories:.0f} kcal"],
                ["Eng yuqori kunlik kaloriya", f"{max_calories} kcal"],
                ["Eng past kunlik kaloriya", f"{min_calories} kcal"],
                ["O'rtacha oqsillar", f"{avg_protein:.1f} g"],
                ["O'rtacha yog'lar", f"{avg_fat:.1f} g"],
                ["O'rtacha uglevodlar", f"{avg_carbs:.1f} g"],
                ["O'rtacha sarflangan kaloriya", f"{avg_calories_burned:.0f} kcal"],
                ["O'rtacha sof kaloriya", f"{avg_net_calories:.0f} kcal"],
                ["Kunlar soni", f"{len(sorted_daily_data)} kun"],
            ]

            # Statistika jadvali
            stats_table = Table(stats_data, colWidths=[80 * mm, 50 * mm])
            stats_table.setStyle(TableStyle([
                # Sarlavha qatori
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
            ]))

            # Juft va toq qatorlar uchun ranglar
            for i in range(1, len(stats_data)):
                if i % 2 == 0:
                    stats_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
                    ]))
                else:
                    stats_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, i), (-1, i), colors.white)
                    ]))

            # Barcha qatorlar uchun umumiy uslub
            stats_table.setStyle(TableStyle([
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('ROWHEIGHT', (0, 0), (-1, -1), 7 * mm),
            ]))

            # Jadvalni PDFga qo'shish
            stats_table.wrapOn(pdf, 130 * mm, 80 * mm)
            stats_table.drawOn(pdf, 20 * mm, y_position - 80 * mm)

            return y_position - 90 * mm  # Keyingi element uchun y pozitsiyasi



        # Ovqat turlari bo'yicha diagramma
        def draw_meal_type_chart(y_position):
            # Diagramma sarlavhasi
            pdf.setFont("Helvetica-Bold", 14)
            pdf.setFillColor(colors.darkblue)
            pdf.drawString(20 * mm, y_position, "Ovqat turlari bo'yicha kaloriyalar")

            if not meal_type_calories:
                pdf.setFont("Helvetica-Italic", 12)
                pdf.drawString(20 * mm, y_position - 20 * mm, "Ma'lumot mavjud emas")
                return y_position - 30 * mm

            # Diagramma yaratish
            drawing = Drawing(page_width - 40 * mm, 80 * mm)

            pie = Pie()
            pie.x = 150
            pie.y = 15
            pie.width = 150
            pie.height = 150

            # Ma'lumotlarni tayyorlash
            pie_data = []
            pie_labels = []

            for meal_type, calories in meal_type_calories.items():
                pie_data.append(calories)
                pie_labels.append(f"{meal_type}")

            pie.data = pie_data
            pie.labels = pie_labels

            # Diagramma uslubi
            pie.slices.strokeWidth = 0.5
            pie.slices.strokeColor = colors.white

            # Ranglar
            pie_colors = [colors.blue, colors.green, colors.red, colors.orange, colors.purple]
            for i in range(len(pie_data)):
                pie.slices[i].fillColor = pie_colors[i % len(pie_colors)]

            drawing.add(pie)

            # Diagrammani PDFga qo'shish
            drawing.wrapOn(pdf, page_width - 40 * mm, 80 * mm)
            drawing.drawOn(pdf, 20 * mm, y_position - 90 * mm)

            # Diagramma izohini qo'shish
            pdf.setFont("Helvetica", 10)
            y_legend = y_position - 95 * mm
            for i, (meal_type, calories) in enumerate(meal_type_calories.items()):
                pdf.setFillColor(pie_colors[i % len(pie_colors)])
                pdf.drawString(30 * mm, y_legend - i * 6 * mm,
                               f"■ {meal_type}: {calories} kcal ({(calories / sum(pie_data) * 100):.1f}%)")

            return y_position - 105 * mm - len(meal_type_calories) * 6 * mm  # Keyingi element uchun y pozitsiyasi

        # Quyi qismni chizish
        def draw_footer():
            # Ajratuvchi chiziq
            pdf.setStrokeColor(colors.darkblue)
            pdf.setLineWidth(1)
            pdf.line(20 * mm, 20 * mm, page_width - 20 * mm, 20 * mm)

            # Footer matni
            pdf.setFont("Helvetica", 8)
            pdf.setFillColor(colors.darkblue)
            pdf.drawCentredString(page_width / 2, 15 * mm, "Salomat ovqatlanish tizimi - Barcha huquqlar himoyalangan")
            pdf.drawCentredString(page_width / 2, 10 * mm, f"© {timezone.now().year} Salomat Ovqatlanish")

            # Sahifa raqami
            pdf.drawRightString(page_width - 20 * mm, 15 * mm, "Sahifa 1")

        # PDF yaratish
        draw_header()
        next_y = draw_daily_summary_table()
        next_y = draw_statistics(next_y)

        # Agar sahifada joy qolmasa, yangi sahifa yaratish
        if next_y < 100 * mm:
            pdf.showPage()
            draw_header()
            next_y = page_height - 60 * mm

        next_y = draw_meal_type_chart(next_y)
        draw_footer()

        pdf.showPage()
        pdf.save()

        # Faylni qaytarish
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response[
            'Content-Disposition'] = f'attachment; filename="kaloriya_statistika_{username}_{start_date}_dan_{end_date}_gacha.pdf"'
        return response

    except Exception as e:
        # Xatolik yuz berganda
        print(f"PDF yaratishda xatolik: {str(e)}")
        return HttpResponse(f"Hisobotni yaratishda xatolik yuz berdi: {str(e)}", status=500)