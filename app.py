from flask import Flask, request, jsonify
from transformers import pipeline
import logging
import time
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize the sentiment analysis pipeline
# Using a lightweight model for faster startup
logger.info("Loading sentiment analysis model...")
start_time = time.time()

try:
    # Using DistilBERT for faster inference
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        tokenizer="distilbert-base-uncased-finetuned-sst-2-english"
    )
    load_time = time.time() - start_time
    logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    sentiment_pipeline = None

@app.route('/')
def home():
    return {
        "service": "Sentiment Analysis API",
        "version": "v1.0",
        "status": "healthy" if sentiment_pipeline else "model_load_failed",
        "endpoints": {
            "/analyze": "POST - Analyze sentiment of text",
            "/batch": "POST - Analyze multiple texts",
            "/health": "GET - Health check",
            "/metrics": "GET - Basic metrics"
        }
    }

@app.route('/health')
def health():
    return {
        "status": "healthy" if sentiment_pipeline else "unhealthy",
        "model_loaded": sentiment_pipeline is not None,
        "timestamp": time.time()
    }

@app.route('/analyze', methods=['POST'])
def analyze_sentiment():
    if not sentiment_pipeline:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field in request body"}), 400
        
        text = data['text']
        if not text.strip():
            return jsonify({"error": "Text cannot be empty"}), 400
        
        # Perform sentiment analysis
        start_time = time.time()
        result = sentiment_pipeline(text)[0]
        inference_time = time.time() - start_time
        
        # Convert to more readable format
        sentiment = result['label'].lower()
        confidence = round(result['score'], 4)
        
        response = {
            "text": text,
            "sentiment": sentiment,
            "confidence": confidence,
            "inference_time_ms": round(inference_time * 1000, 2)
        }
        
        logger.info(f"Analyzed text: '{text[:50]}...' -> {sentiment} ({confidence})")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/batch', methods=['POST'])
def batch_analyze():
    if not sentiment_pipeline:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({"error": "Missing 'texts' field in request body"}), 400
        
        texts = data['texts']
        if not isinstance(texts, list):
            return jsonify({"error": "'texts' must be a list"}), 400
        
        if len(texts) > 10:  # Limit batch size
            return jsonify({"error": "Maximum 10 texts per batch"}), 400
        
        # Perform batch sentiment analysis
        start_time = time.time()
        results = sentiment_pipeline(texts)
        inference_time = time.time() - start_time
        
        # Format results
        formatted_results = []
        for i, (text, result) in enumerate(zip(texts, results)):
            formatted_results.append({
                "text": text,
                "sentiment": result['label'].lower(),
                "confidence": round(result['score'], 4)
            })
        
        response = {
            "results": formatted_results,
            "count": len(texts),
            "total_inference_time_ms": round(inference_time * 1000, 2)
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/metrics')
def metrics():
    return {
        "model": "distilbert-base-uncased-finetuned-sst-2-english",
        "framework": "transformers",
        "python_version": os.sys.version,
        "model_loaded": sentiment_pipeline is not None
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
