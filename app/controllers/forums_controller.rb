class ForumsController < ApplicationController
  def index
    @forums = Forum.all

    # Trier les forums par nombre de visites en ordre décroissant
    @forums_by_visits = @forums.order(visits: :desc)

    # Trier les forums par date de publication en ordre décroissant
    @forums_by_date = @forums.order(pub: :desc)

    # Calculer le nombre de forums pour chaque statut
    total_count = @forums.size
    published_count = @forums.where(status: 'PUBLISHED').count
    not_published_count = @forums.where(status: 'NOT PUBLISHED').count

    # Calculer les pourcentages 
    published_percentage = (published_count.to_f / total_count * 100).round(2)
    not_published_percentage = (not_published_count.to_f / total_count * 100).round(2)
    Rails.logger.info("x: #{published_count}")
    Rails.logger.info("x: #{published_percentage}")
    Rails.logger.info("b: #{not_published_percentage}")

    # Préparer les données pour le graphique en secteurs
    @status_data = [
      { name: 'Published', y: published_percentage },
      { name: 'Not Published', y: not_published_percentage }
    ]

    # Préparer les données pour le graphique linéaire
    @monthly_data = aggregate_data_by_month
    Rails.logger.info("sssssssssssssssssszs: #{@monthly_data}")

  end

  private

  def aggregate_data_by_month
    # Initialiser un hash pour stocker les résultats
    monthly_counts = Hash.new(0)
    
    # Parcourir chaque forum et calculer les visites par mois
    @forums.each do |forum|
      next unless forum.pub.present?

      month_year = forum.pub.strftime('%b %Y')
      monthly_counts[month_year] += 1
    end

    # Trier les résultats par mois
    sorted_monthly_counts = monthly_counts.sort_by { |month, _| Date.parse(month) }
    
    # Extraire les mois et les valeurs
    months = sorted_monthly_counts.map(&:first)
    values = sorted_monthly_counts.map(&:last)
    
    { months: months, values: values }
  end
end
